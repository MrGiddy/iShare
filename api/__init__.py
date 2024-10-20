from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from .config import Config
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Load the configuration
    app.config.from_object(Config)

    # Initialize the database and bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # Initialize JWT
    jwt.init_app(app)

    from api.models.tokenblacklist import TokenBlacklist

    # Register JWT token blacklist checker
    @jwt.token_in_blocklist_loader
    def check_if_token_is_blacklisted(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

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
