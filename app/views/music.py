from flask import Blueprint, render_template, request, redirect
from app import db
import base64
import json
from app.models import Music, LyricFiles, Score
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