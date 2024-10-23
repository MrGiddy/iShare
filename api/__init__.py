from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_swagger_ui import get_swaggerui_blueprint
from .config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()


# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Path to the API documentation file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static url
    API_URL,      # Swagger UI doc path
    config={
        'app_name': "iShare API"
    }
)


def create_app():
    app = Flask(__name__)

    # Load the configuration
    app.config.from_object(Config)

    # Configure cors
    CORS(app, resources={r"*": {"origins": "*"}})

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
    from api.routes.admin_routes import admin_bp

    app.register_blueprint(base_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(picture_bp, url_prefix='/api')
    app.register_blueprint(comment_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
