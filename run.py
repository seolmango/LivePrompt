from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

import config

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy()
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

socket = SocketIO(app, async_mode='eventlet')

from models.views import main, user, music, setlist, control, live
app.register_blueprint(main.bp)
app.register_blueprint(user.bp)
app.register_blueprint(music.bp)
app.register_blueprint(setlist.bp)
app.register_blueprint(control.bp)
app.register_blueprint(live.bp)

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

if __name__ == '__main__':
    socket.run(app, host='0.0.0.0', port=8000, debug=True)