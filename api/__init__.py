from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from .config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    # Load the configuration
    app.config.from_object(Config)

    # Initialize the database and bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints (routes)
    from api.routes.base_routes import base_bp
    from api.routes.user_routes import user_bp
    from api.routes.picture_routes import picture_bp
    from api.routes.comment_routes import comment_bp

    app.register_blueprint(base_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(picture_bp)
    app.register_blueprint(comment_bp)

    return app
