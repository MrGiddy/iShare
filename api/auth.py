from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from api.models.user import User
from api import bcrypt
from functools import wraps


def authenticate_user(email, password):
    """autenticate a user"""
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return user
    return


def generate_token(user):
    """create an access token"""
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return access_token


def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as err:
            return jsonify({"error": "Invalid token"}), 401
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                if not user or user.role != role:
                    return jsonify({"error": "Insufficient permissions"}), 403
                return f(*args, **kwargs)
            except Exception as err:
                return jsonify({"error": "Invalid token"}), 401
        return decorated_function
    return decorator
