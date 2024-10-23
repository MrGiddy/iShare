#!/usr/bin/env python3
import os
from flask import Blueprint, request, jsonify
from api import db
from api.auth import authenticate_user, generate_token, role_required
from api.models.tokenblacklist import TokenBlacklist
from api.models.user import User
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity


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
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    # Return a success message
    return jsonify({"message": "User registered successfully!"}), 201


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
    return jsonify({"message": "Login successful!", "access_token": access_token})


@user_bp.route('/logout', methods=['POST'], endpoint='logout')
@jwt_required()
def logout():
    """Logout the user by blacklisting their JWT token"""
    jti = get_jwt()['jti']
    token_blacklist = TokenBlacklist(jti=jti)
    db.session.add(token_blacklist)
    db.session.commit()

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
    return jsonify({
    "message": "Profile retrieved successfully",
    "user": {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    }), 200


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
            db.session.refresh(user)

    db.session.commit()
    return jsonify({
        "message": "User profile updated successfully!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }}), 200


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
    return jsonify({"message": "User account deleted successfully!"}), 200


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
