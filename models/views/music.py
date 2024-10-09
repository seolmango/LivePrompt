from flask import Blueprint, render_template, request, redirect
from run import db
import base64
import json
from models.models import Music, LyricFiles, Score, Setlist
bp = Blueprint('music', __name__, url_prefix='/music')

@bp.route('/')
def index():
    musics = Music.query.all()
    data = []
    for music in musics:
        temp = {}
        temp['id'] = music.id
        temp['title'] = music.title
        temp['artist'] = music.artist
        temp['time'] = music.length
        data.append(temp)
    return render_template('music/music-index.html', musics=data)

@bp.route('/add', methods=['GET'])
def add():
    return render_template('music/musicadd.html')

@bp.route('/delete', methods=['GET'])
def delete():
    return render_template('music/musicdelete.html')

@bp.route('/addmusic', methods=['POST'])
def add_music():
    music = Music(title=request.form['title'], artist=request.form['artist'], length=request.form['time'])
    db.session.add(music)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/deletemusic', methods=['POST'])
def delete_music():
    music = Music.query.filter_by(id=request.form['musicid']).first()
    setlists = Setlist.query.all()
    for setlist in setlists:
        data = json.loads(setlist.setlist_songs)
        if music.title in data:
            data.remove(music.title)
            setlist.setlist_songs = json.dumps(data)
            db.session.commit()
        data = json.loads(setlist.setlist_data)
        for song in data:
            if music.id == song['music']:
                data.remove(song)
        setlist.setlist_data = json.dumps(data)
        db.session.commit()
    db.session.delete(music)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/<int:music_id>', methods=['GET'])
def detail(music_id):
    music = Music.query.filter_by(id=music_id).first()
    data = {}
    data['id'] = music.id
    data['title'] = music.title
    data['artist'] = music.artist
    data['time'] = music.length
    lyrics = LyricFiles.query.filter_by(file_music_id=music.id).all()
    data['lyrics'] = []
    for lyric in lyrics:
        temp = {}
        temp['id'] = lyric.id
        temp['name'] = lyric.lyric_name
        temp['prev'] = lyric.content[:20]
        data['lyrics'].append(temp)
    scores = Score.query.filter_by(score_music_id=music.id).all()
    data['scores'] = []
    for score in scores:
        temp = {}
        temp['id'] = score.id
        temp['name'] = score.score_name
        temp['page'] = len(json.loads(base64.b64decode(score.content).decode('utf-8')))
        data['scores'].append(temp)
    return render_template('music/detail.html', music=data)

@bp.route('/edit/<int:music_id>', methods=['POST'])
def edit(music_id):
    music = Music.query.filter_by(id=music_id).first()
    music.title = request.form['title']
    music.artist = request.form['artist']
    music.length = request.form['time']
    db.session.commit()
    return redirect('/music/' + str(music_id))

@bp.route('/<int:music_id>/addlyrics', methods=['GET'])
def add_lyric(music_id):
    return render_template('music/addlyrics.html', music_id=music_id)

@bp.route('/<int:music_id>/addlyricspost', methods=['POST'])
def add_lyric_post(music_id):
    lyric = LyricFiles(lyric_name=request.form['nickname'], file_music_id=music_id, content=request.form['content'])
    db.session.add(lyric)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/<int:music_id>/deletelyrics', methods=['GET'])
def delete_lyric(music_id):
    return render_template('music/deletelyrics.html', music_id=music_id)

@bp.route('/<int:music_id>/deletelyricspost', methods=['POST'])
def delete_lyric_post(music_id):
    lyric = LyricFiles.query.filter_by(id=request.form['lyrics_id']).first()
    setlists = Setlist.query.all()
    for setlist in setlists:
        data = json.loads(setlist.setlist_data)
        for song in data:
            if song['music'] == music_id:
                for user in song['data']:
                    if song['data'][user]['type'] == 'lyrics' and song['data'][user]['id'] == lyric.id:
                        song['data'][user]['type'] = 'none'
                        song['data'][user]['id'] = 0
        setlist.setlist_data = json.dumps(data)
    db.session.delete(lyric)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/lyric/<int:lyric_id>', methods=['GET'])
def lyric(lyric_id):
    lyric = LyricFiles.query.filter_by(id=lyric_id).first()
    data = {}
    data['id'] = lyric.id
    data['name'] = lyric.lyric_name
    data['content'] = lyric.content
    return render_template('music/lyric.html', lyric=data)

@bp.route('/lyric/edit/<int:lyric_id>', methods=['POST'])
def lyric_edit(lyric_id):
    lyric = LyricFiles.query.filter_by(id=lyric_id).first()
    lyric.lyric_name = request.form['nickname']
    lyric.content = request.form['content']
    db.session.commit()
    return redirect('/music/lyric/' + str(lyric_id))

@bp.route('/<int:music_id>/addscore', methods=['GET'])
def add_score(music_id):
    return render_template('music/addscore.html', music_id=music_id)

@bp.route('/<int:music_id>/addscorepost', methods=['POST'])
def add_score_post(music_id):
    files = request.files.getlist('file[]')
    start_times = request.form.getlist('start_time[]')
    end_times = request.form.getlist('end_time[]')

    content = []
    for i in range(len(files)):
        file = files[i]
        start_time = start_times[i]
        end_time = end_times[i]
        content.append({'file': f"data:{file.mimetype};base64, {base64.b64encode(file.read()).decode('utf-8')}", 'start_time': start_time, 'end_time': end_time})
    json_content = json.dumps(content)
    score = Score(score_name=request.form['nickname'], score_music_id=music_id, content=base64.b64encode(json_content.encode('utf-8')))

    db.session.add(score)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/<int:music_id>/deletescore', methods=['GET'])
def delete_score(music_id):
    return render_template('music/deletescore.html', music_id=music_id)

@bp.route('/<int:music_id>/deletescorepost', methods=['POST'])
def delete_score_post(music_id):
    score = Score.query.filter_by(id=request.form['score_id']).first()
    setlists = Setlist.query.all()
    for setlist in setlists:
        data = json.loads(setlist.setlist_data)
        for song in data:
            if song['music'] == music_id:
                for user in song['data']:
                    if song['data'][user]['type'] == 'score' and song['data'][user]['id'] == score.id:
                        song['data'][user]['type'] = 'none'
                        song['data'][user]['id'] = 0
        setlist.setlist_data = json.dumps(data)
    db.session.delete(score)
    db.session.commit()
    return render_template('windowclose.html')

@bp.route('/score/<int:score_id>', methods=['GET'])
def score(score_id):
    score = Score.query.filter_by(id=score_id).first()
    data = {}
    data['id'] = score.id
    data['name'] = score.score_name
    data['content'] = json.loads(base64.b64decode(score.content.decode('utf-8')))
    content = []
    for i in range(len(data['content'])):
        temp = {}
        temp['start_time'] = data['content'][i]['start_time']
        temp['end_time'] = data['content'][i]['end_time']
        temp['img_data'] = data['content'][i]['file']
        content.append(temp)
    data['content'] = content
    return render_template('music/score.html', score=data)

@bp.route('/score/edit/<int:score_id>', methods=['POST'])
def score_edit(score_id):
    score = Score.query.filter_by(id=score_id).first()
    start_times = request.form.getlist('start_time[]')
    end_times = request.form.getlist('end_time[]')

    content = json.loads(base64.b64decode(score.content.decode('utf-8')))
    for i in range(len(content)):
        content[i]['start_time'] = start_times[i]
        content[i]['end_time'] = end_times[i]

    score.score_name = request.form['nickname']
    json_content = json.dumps(content)
    score.content = base64.b64encode(json_content.encode('utf-8'))
    db.session.commit()
    return redirect('/music/score/' + str(score_id))
