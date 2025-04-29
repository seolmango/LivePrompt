from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

import config

app = Flask(__name__, template_folder='models/templates', static_folder='models/static')
app.config.from_object(config)

@app.before_request
def enforce_https():
    if not request.is_secure:
        return redirect(request.url.replace("http://", "https://", 1), code=301)

db = SQLAlchemy()
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

socketio = SocketIO(app, async_mode='eventlet')
socketio.init_app(app)

from models.views import main, user, music, setlist, control, live
app.register_blueprint(main.bp)
app.register_blueprint(user.bp)
app.register_blueprint(music.bp)
app.register_blueprint(setlist.bp)
app.register_blueprint(control.bp)
app.register_blueprint(live.bp)
