from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import main, user, music
    app.register_blueprint(main.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(music.bp)

    return app