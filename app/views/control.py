import base64
from flask import Blueprint, render_template, send_from_directory, current_app, request
from app import socket, status
from flask_socketio import emit
import os, json
from app.models import Setlist, Music, User, Score, LyricFiles
import time
from threading import Thread

bp = Blueprint('control', __name__, url_prefix='/control')

def save_json_to_file(data, filename):
    if not os.path.exists(current_app.config['JSON_FOLDER']):
        os.makedirs(current_app.config['JSON_FOLDER'])

    file_path = os.path.join(current_app.config['JSON_FOLDER'], filename)
    fake_file_path = '/control/file/' + filename
    with open(file_path, 'w') as f:
        json.dump(data, f)

    return fake_file_path

def run():
    while True:
        if status['is_playing']:
            time.sleep(1)
            if status['time'] < status['time_length'][status['music_index']]:
                status['time'] += 1
                for user in status['sockets'].keys():
                    for s in status['sockets'][user]:
                        socket.emit('time_update', status['time'], room=s)
            else:
                if status['music_index'] == status['setlist_length'] - 1:
                    status['music_index'] = 0
                else:
                    status['music_index'] += 1
                status['time'] = 0
                for user in status['sockets'].keys():
                    for s in status['sockets'][user]:
                        socket.emit('next', room=s)
                        socket.emit('time_update', 0, room=s)
        else:
            break

@bp.route('/')
def index():
    setlists = Setlist.query.all()
    data = []
    for setlist in setlists:
        data.append({
            'id': setlist.id,
            'name': setlist.setlist_name
        })
    return render_template('control/index.html', setlists=data)

@bp.route('/file/<filename>')
def serve_file(filename):
    if(filename == ''):
        return 'File not found', 404
    file_list = os.listdir(current_app.config['JSON_FOLDER'])
    if filename in file_list:
        return send_from_directory(current_app.config['JSON_FOLDER'], filename)
    else:
        return 'File not found', 404

@bp.route('/screen/<id>')
def screen(id):
    user = User.query.filter_by(id=id).first()
    data = {
        'id': user.id,
        'nickname': user.nickname
    }
    return render_template('control/screen.html', user=data)

@socket.on('disconnect')
def disconnect():
    if request.sid in status['sockets']:
        for user in status['sockets'].keys():
            if request.sid in status['sockets'][user]:
                status['sockets'][user].remove(request.sid)

@socket.on('control_init')
def control_init():
    status['sockets']['control'].append(request.sid)
    if status['setlist'] is None:
        emit('none_setlist')
        return
    emit('init_data', [status['datas']['control'], status['music_index'], status['time'], status['is_playing']])

@socket.on('screen_init')
def screen_init(id):
    if id not in status['sockets']:
        status['sockets'][id] = []
    status['sockets'][id].append(request.sid)
    if status['setlist'] is None:
        emit('none_setlist')
        return
    if str(id) not in status['datas'].keys():
        emit('not_include')
        return
    emit('init_data', [status['datas'][str(id)], status['music_index'], status['time'], status['is_playing']])

@socket.on('control_start')
def control_start():
    status['is_playing'] = True
    Thread(target=run).start()
    for user in status['sockets'].keys():
        for s in status['sockets'][user]:
            emit('start', room=s)

@socket.on('control_stop')
def control_stop():
    status['is_playing'] = False
    for user in status['sockets'].keys():
        for s in status['sockets'][user]:
            emit('stop', room=s)


@socket.on('control_next')
def control_next():
    if status['music_index'] == status['setlist_length'] - 1:
        status['music_index'] = 0
    else:
        status['music_index'] += 1
    status['time'] = 0
    status['is_playing'] = False
    for user in status['sockets'].keys():
        for s in status['sockets'][user]:
            emit('next', room=s)
            emit('time_update', 0, room=s)
            emit('stop', room=s)


@socket.on('control_prev')
def control_prev():
    if status['time'] == 0:
        if status['music_index'] == 0:
            status['music_index'] = status['setlist_length'] - 1
        else:
            status['music_index'] -= 1
        status['time'] = 0
        status['is_playing'] = False
        for user in status['sockets'].keys():
            for s in status['sockets'][user]:
                emit('prev', room=s)
                emit('time_update', 0, room=s)
                emit('stop', room=s)
    else:
        status['time'] = 0
        status['is_playing'] = False
        for user in status['sockets'].keys():
            for s in status['sockets'][user]:
                emit('time_update', 0, room=s)
                emit('stop', room=s)


@socket.on('control_set_index')
def control_set_index(index):
    status['music_index'] = index
    status['time'] = 0
    status['is_playing'] = False
    for user in status['sockets'].keys():
        for s in status['sockets'][user]:
            emit('set_index', index, room=s)
            emit('time_update', 0, room=s)
            emit('stop', room=s)

@socket.on('control_set_list')
def control_set_list(id):
    if id == '0':
        status['setlist'] = None
        status['setlist_length'] = None
        status['is_playing'] = False
        status['music_index'] = 0
        status['time'] = 0
        for user in status['sockets'].keys():
            for s in status['sockets'][user]:
                emit('none_setlist', room=s)
        return
    setlist = Setlist.query.filter_by(id=id).first()
    status['setlist'] = id
    status['setlist_length'] = len(setlist.setlist_songs.split(','))
    status['is_playing'] = False

    status['datas'], status['time_length'] = data_make(id)
    status['music_index'] = 0
    status['time'] = 0

    for user in status['sockets'].keys():
        if str(user) in status['datas'].keys():
            for s in status['sockets'][user]:
                emit('init_data', [status['datas'][str(user)], status['music_index'], status['time'], status['is_playing']], room=s)
        else:
            for s in status['sockets'][user]:
                emit('not_include', room=s)

def data_make(id):
    setlist = Setlist.query.filter_by(id=id).first()
    setlist_screen_Data = json.loads(setlist.setlist_data)

    length = []
    control_Data = []
    users_list = []
    users_Data = []

    first_song = setlist_screen_Data[0]['data']
    for i in first_song.keys():
        users_list.append(i)
        users_Data.append([])

    for i in setlist_screen_Data:
        music = Music.query.filter_by(id=i['music']).first()
        length.append(music.length)
        control_Data.append({
            'title': music.title,
            'artist': music.artist,
            'duration': music.length
        })
        music_data = i['data']
        for user_index, user in enumerate(users_list):
            if music_data[user]['type'] == "score":
                score = Score.query.filter_by(id=music_data[user]['id']).first()
                users_Data[user_index].append({
                    'title': music.title,
                    'artist': music.artist,
                    'duration': music.length,
                    'type': 'score',
                    'content': json.loads(base64.b64decode(score.content.decode('utf-8')))
                })
            elif music_data[user]['type'] == "lyric":
                lyric = LyricFiles.query.filter_by(id=music_data[user]['id']).first()
                users_Data[user_index].append({
                    'title': music.title,
                    'artist': music.artist,
                    'duration': music.length,
                    'type': 'lyric',
                    'content': lyric.content
                })
            else:
                users_Data[user_index].append({
                    'title': music.title,
                    'artist': music.artist,
                    'duration': music.length,
                    'type': 'none',
                    'content': None
                })

    for file in os.listdir(current_app.config['JSON_FOLDER']):
        os.remove(os.path.join(current_app.config['JSON_FOLDER'], file))

    data ={}
    control_file = save_json_to_file(control_Data, 'control.json')
    data['control'] = control_file
    for i, user in enumerate(users_list):
        user_file = save_json_to_file(users_Data[i], f'{user}.json')
        data[user] = user_file

    return data, length