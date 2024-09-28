from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

import config

db = SQLAlchemy()
migrate = Migrate()
socket = SocketIO()

status = {
    'setlist': None,
    'music_index': None,
    'setlist_length': None,
    'time': None,
    'time_length': None,
    'is_playing': False,
    'datas' : {},
    'sockets' : {
        'control': []
    },
    'lock' : None
}

def create_app():
    app = Flask(__name__)  # Define app here
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import main, user, music, setlist, control
    app.register_blueprint(main.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(music.bp)
    app.register_blueprint(setlist.bp)
    app.register_blueprint(control.bp)

    socket.init_app(app)
    return app  # Return app here
