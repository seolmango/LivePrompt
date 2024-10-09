from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

import config

app = Flask(__name__, template_folder='models/templates', static_folder='models/static')
app.config.from_object(config)

db = SQLAlchemy()
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

socketio = SocketIO(app, async_mode='eventlet')

from models.views import main, user, music, setlist, control, live
app.register_blueprint(main.bp)
app.register_blueprint(user.bp)
app.register_blueprint(music.bp)
app.register_blueprint(setlist.bp)
app.register_blueprint(control.bp)
app.register_blueprint(live.bp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)