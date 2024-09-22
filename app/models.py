from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True, nullable=False)

class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    lyrics = db.relationship('LyricFiles', backref='music', lazy=True)
    scores = db.relationship('Score', backref='music', lazy=True)
    length = db.Column(db.Integer, nullable=False)

class LyricFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    row_file_path = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    row_file_path = db.Column(db.String(300), nullable=False)
    content = db.Column(db.LargeBinary, nullable=False)