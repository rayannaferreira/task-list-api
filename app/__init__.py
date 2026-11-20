import os

from flask import Flask
from flask_cors import CORS

from .db import db, migrate
from .models import task, goal
from .routes.task_routes import bp as tasks_bp
from .routes.goal_routes import bp as goals_bp


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

    if config:
        # Allow tests to override the default settings.
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(tasks_bp)
    app.register_blueprint(goals_bp)

    return app
