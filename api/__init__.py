from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from .config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # Load the configuration
    app.config.from_object(Config)

    # Initialize the database and bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    # Initialize JWT
    jwt.init_app(app)

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    from api.models.tokenblacklist import TokenBlacklist

    # Register JWT token blacklist checker
    @jwt.token_in_blocklist_loader
    def check_if_token_is_blacklisted(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "The token has been revoked, please login again"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Your token has expired, please login again"}), 401

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
