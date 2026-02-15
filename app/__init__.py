from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    db.init_app(app)

    # Blueprint registration will be added here
    # from app.routes import todo_bp
    # app.register_blueprint(todo_bp)

    return app
