from flask import Blueprint, render_template, request, redirect
from app import db
from models.models import Music, User, Setlist
import json


bp = Blueprint('setlist', __name__, url_prefix='/setlist')


@bp.route('/')
def index():
    lists = Setlist.query.all()
    data = []
    for l in lists:
        data.append({
            'id': l.id,
            'name': l.setlist_name,
            'headcount': len(json.loads(l.setlist_users)),
            'song_count': len(json.loads(l.setlist_songs)),
        })
        # data.append({
        #     'id': l.id,
        #     'name': l.setlist_name,
        #     'headcount': 0,
        #     'song_count': 0,
        # })
    return render_template('setlist/setlist-index.html', setlists=data)

@bp.route('/delete', methods=['GET'])
def delete():
    return render_template('setlist/deletesetlist.html')

@bp.route('/deletesetlist', methods=['POST'])
def delete_setlist():
    setlist = Setlist.query.filter_by(id=request.form['setid']).first()
    db.session.delete(setlist)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/make', methods=['GET'])
def make():
    users = User.query.all()
    musics = Music.query.all()
    string_users = []
    for user in users:
        string_users.append({
            'id': user.id,
            'name': user.nickname,
        })
    string_users = str(string_users).replace("'", '"')
    music = []
    for music_data in musics:
        temp = {}
        temp['id'] = music_data.id
        temp['title'] = music_data.title

        Lyrics = music_data.lyrics
        temp['lyrics'] = []
        for lyric in Lyrics:
            temp['lyrics'].append({
                'id': lyric.id,
                'name': lyric.lyric_name,
            })

        Scores = music_data.scores
        temp['scores'] = []
        for score in Scores:
            temp['scores'].append({
                'id': score.id,
                'name': score.score_name,
            })
        music.append(temp)
    string_music = str(music).replace("'", '"')
    return render_template('setlist/makesetlist.html', users=users, musics=music, jsuser=string_users, jsmusic=string_music)

@bp.route('/makenew', methods=['POST'])
def make_new():
    setlist = Setlist()
    setlist.setlist_name = request.form.get('name')
    setlist.setlist_users = request.form.get('users')
    setlist.setlist_songs = request.form.get('songs')
    setlist.setlist_data = request.form.get('data')
    db.session.add(setlist)
    db.session.commit()
    return redirect('/setlist')

@bp.route('/<int:setlist_id>')
def view_setlist(setlist_id):
    setlist = Setlist.query.filter_by(id=setlist_id).first()
    table_users = json.loads(setlist.setlist_users)
    table_songs = json.loads(setlist.setlist_songs)
    table_data = json.loads(setlist.setlist_data)

    users = User.query.all()
    musics = Music.query.all()
    string_users = []
    for user in users:
        string_users.append({
            'id': user.id,
            'name': user.nickname,
        })
    string_users = str(string_users).replace("'", '"')
    music = []
    for music_data in musics:
        temp = {}
        temp['id'] = music_data.id
        temp['title'] = music_data.title

        Lyrics = music_data.lyrics
        temp['lyrics'] = []
        for lyric in Lyrics:
            temp['lyrics'].append({
                'id': lyric.id,
                'name': lyric.lyric_name,
            })

        Scores = music_data.scores
        temp['scores'] = []
        for score in Scores:
            temp['scores'].append({
                'id': score.id,
                'name': score.score_name,
            })
        music.append(temp)
    string_music = str(music).replace("'", '"')
    return render_template('setlist/detail.html', setlist_id=setlist_id, name=setlist.setlist_name, table_users=table_users, table_songs=table_songs, table_data=table_data, users=users, musics=music, jsuser=string_users, jsmusic=string_music)

@bp.route('/edit/<int:setlist_id>', methods=['POST'])
def edit_setlist(setlist_id):
    setlist = Setlist.query.filter_by(id=setlist_id).first()
    setlist.setlist_name = request.form.get('name')
    setlist.setlist_users = request.form.get('users')
    setlist.setlist_songs = request.form.get('songs')
    setlist.setlist_data = request.form.get('data')
    db.session.commit()
    return redirect('/setlist')