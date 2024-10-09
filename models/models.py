from models import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True, nullable=False)

class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    lyrics = db.relationship('LyricFiles', backref='music', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='music', lazy=True, cascade="all, delete-orphan")
    length = db.Column(db.Integer, nullable=False)

class LyricFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lyric_name = db.Column(db.String(128), nullable=False)
    file_music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_name = db.Column(db.String(128), nullable=False)
    score_music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)

class Setlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setlist_name = db.Column(db.String(128), nullable=False)
    setlist_users = db.Column(db.Text, nullable=False)
    setlist_songs = db.Column(db.Text, nullable=False)
    setlist_data = db.Column(db.Text, nullable=False)