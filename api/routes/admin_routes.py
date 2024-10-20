from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from api import db
from api.auth import role_required
from api.models.comment import Comment
from api.models.picture import Picture
from api.models.user import User


admin_bp = Blueprint('admin_bp', __name__)


# Get all users
@admin_bp.route('/users', methods=['GET'], endpoint='get_all_users')
@jwt_required()
@role_required('admin')
def get_all_users():
    """retrieve all users from database"""
    users = User.query.all()
    users_list = []
    users_list = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    } for user in users]

    return jsonify(users_list), 200


@admin_bp.route('/pictures', methods=['GET'], endpoint='get_all_pictures')
@jwt_required()
@role_required('admin')
def get_all_pictures():
    """retrieve all pictures across all users"""
    pictures = Picture.query.all()
    return jsonify([
        {
            "id": picture.id,
            "user_id": picture.user_id,
            "image_url": picture.image_url,
            "description": picture.description,
            "created_at": picture.created_at,
            "updated_at": picture.updated_at
        } for picture in pictures
    ]), 200


# GET: Retrieve all the comments of a specific user
@admin_bp.route('/user/<int:user_id>/comments', methods=['GET'], endpoint="get_user_comments")
@role_required('admin')
def get_user_comments(user_id):
    """retrieve all comments of a specific user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    comments = Comment.query.filter_by(user_id=user_id).all()
    comments_list = [{
        "id": comment.id,
        "user_id": comment.user_id,
        "picture_id": comment.picture_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    } for comment in comments]

    return jsonify(comments_list), 200


@admin_bp.route('/promote-user/<int:user_id>', methods=['PUT'], endpoint='make_admin')
@jwt_required()
@role_required('admin')
def make_admin(user_id):
    """give a user admin privileges"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == 'admin':
        return jsonify({"message": "User is already an admin"}), 400

    user.role = 'admin'
    db.session.commit()

    return jsonify({"message": f"User {user.username} promoted to admin!"}), 200


@admin_bp.route('/demote-user/<int:user_id>', methods=['PUT'], endpoint='demote_admin')
@jwt_required()
@role_required('admin')
def demote_admin(user_id):
    """revoke admin privileges of a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == 'user':
        return jsonify({"message": "User is already a regular"}), 400

    user.role = 'user'
    db.session.commit()

    return jsonify({"message": f"User {user.username} demoted to regular user!"}), 200
