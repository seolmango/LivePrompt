from flask import Blueprint, render_template, request
from app import db
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