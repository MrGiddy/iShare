#!/usr/bin/env python3
import os
from flask import Blueprint, request, jsonify
from api import db
from api.auth import authenticate_user, generate_token, role_required
from api.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity


# Create a Blueprint for user-related routes
user_bp = Blueprint('user_bp', __name__)


# Registration route
@user_bp.route('/register', methods=['POST'], endpoint='register')
def register():
    """register a user"""
    # Get sign up info from request object
    data = request.get_json()

    # Extract user data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if the username or email is already taken
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"error": "User with this email or username already exists"}), 400

    # Create a new user and save to database
    new_user = User()
    new_user.username = username
    new_user.email = email
    # new_user.role = 'admin'
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # Return a success message
    return jsonify({"message": "User registerd successfully!"}), 201


# Login route
@user_bp.route('/login', methods=['POST'], endpoint='login')
def login():
    """login a User"""
    # Get login info from request object
    data = request.get_json()

    # Extract user data
    email = data.get('email')
    password = data.get('password')

    # authenticate user by email and password
    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = generate_token(user)
    return jsonify(access_token=access_token), 200


@user_bp.route('/logout', methods=['POST'], endpoint='logout')
@jwt_required()
def logout():
    # Logic to handle logout (e.t., clearing session)
    return jsonify({"message": "Logged out successfully!"})


# Get current User's profile
@user_bp.route('/user', methods=['GET'], endpoint='get_user_profile')
@jwt_required()
def get_user_profile():
    """retrieve current user's profile"""
    current_user_id = get_jwt_identity()

    # Retrieve a user from the database
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return user details (except password_hash)
    user_profile = {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
    return jsonify(user_profile), 200


# Update current User's profile
@user_bp.route('/user', methods=['PUT'], endpoint='update_user_profile')
@jwt_required()
def update_user_profile():
    """update a user's profile"""
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"})

    data = request.get_json()

    username = data.get('username')
    email = data.get('email')

    # Check if the new username or email is already taken
    if username:
        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username and user_by_username.id != current_user_id:
            return jsonify({"error": "Username already exists"}), 400
        else:
            user.username = username

    if email:
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email and user_by_email.id != current_user_id:
            return jsonify({"error": "Email already exists"}), 400
        else:
            user.email = email

    db.session.commit()
    return jsonify({"message": "User profile updated successfully!"}), 200


# Delete current user
@user_bp.route('/user', methods=['DELETE'], endpoint='delete_user')
@jwt_required()
def delete_user():
    """delete the current user"""
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user's pictures from the file system
    for picture in user.pictures:
        if os.path.exists(picture.image_url):
            os.remove(picture.image_url)

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"}), 200


# Get all users
@user_bp.route('/users', methods=['GET'], endpoint='get_all_users')
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


# Change Password
@user_bp.route('/change-password', methods=['PUT'], endpoint='change_password')
@jwt_required()
def change_password():
    """change a user's password"""
    current_user_id = get_jwt_identity()

    # Retrieve user from db by user_id
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Extract password from request object
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Check if current_password matches one in database
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is not correct"}), 400

    # Change the password
    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully!"}), 200


# Reset forgotten password
@user_bp.route('/forgot-password', methods=['POST'], endpoint='forgot_password')
def forgot_password():
    """reset a user's forgotten password"""
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No user with that email found"}), 404

    # Placeholder for email-based password reset functionality
    # Example: Generate a reset token, send via email
    # return jsonify({"message": "Password reset email sent!"}), 200
    return jsonify({"message": "Password reset functionality not yet implemented."})


@user_bp.route('/promote-user/<int:user_id>', methods=['PUT'], endpoint='promote_user')
@jwt_required()
@role_required('admin')
def promote_user(user_id):
    """give a user admin privileges"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == 'admin':
        return jsonify({"message": "User is already an admin"}), 400

    user.role = 'admin'
    db.session.commit()

    return jsonify({"message": f"User {user.username} promoted to admin!"}), 200


@user_bp.route('/demote-user/<int:user_id>', methods=['PUT'], endpoint='demote_admin')
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
