#!/usr/bin/env python3
import os
from flask import Blueprint, request, jsonify
from api import db, bcrypt
from api.models.user import User


# Create a Blueprint for user-related routes
user_bp = Blueprint('user_bp', __name__)


# Registration route
@user_bp.route('/register', methods=['POST'])
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

    # Hash the password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user and save to database
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    # Return a success message
    return jsonify({"message": "User registerd successfully!"}), 201


# Login route
@user_bp.route('/login', methods=['POST'])
def login():
    """login a User"""
    # Get login info from request object
    data = request.get_json()

    # Extract user data
    email = data.get('email')
    password = data.get('password')

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    good_password = bcrypt.check_password_hash(user.password_hash, password)
    if user and good_password:
        return jsonify({"message": f"Welcome {user.username}!"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@user_bp.route('/logout', methods=['POST'])
def logout():
    # Logic to handle logout (e.t., clearing session)
    # return jsonify({"message": "Logged out successfully!"})
    return jsonify({"message": "Logging out not implemented"})


# Get a User's profile
@user_bp.route('/user/<int:user_id>', methods=['GET'], endpoint='get_user_profile')
def get_user_profile(user_id):
    """retrieve a user's profile"""
    # Retrieve a user from the database
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return user details (except password_hash)
    user_profile = {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
    return jsonify(user_profile), 200


# Update a User's profile
@user_bp.route('/user/<int:user_id>', methods=['PUT'], endpoint='update_user_profile')
def update_user_profile(user_id):
    """update a user's profile"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"})

    data = request.get_json()

    username = data.get('username')
    email = data.get('email')

    # Check if the new username or email is already taken
    if username:
        user_by_username = User.query.filter_by(username=username).first()
        print(user_by_username)
        if user_by_username and user_by_username.id != user_id:
            return jsonify({"error": "Username already exists"}), 400
        else:
            user.username = username

    if email:
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email and user_by_email.id != user_id:
            return jsonify({"error": "Email already exists"}), 400
        else:
            user.email = email

    db.session.commit()
    return jsonify({"message": "User profile updated successfully!"}), 200


# Delete a User
@user_bp.route('/user/<int:user_id>', methods=['DELETE'], endpoint='delete_user')
def delete_user(user_id):
    """delete a user"""
    user = User.query.get(user_id)
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
def get_all_users():
    """retrieve all users from database"""
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

    return jsonify(users_list), 200


# Change Password
@user_bp.route('/user/<int:user_id>/change-password', methods=['PUT'], endpoint='change_password')
def change_password(user_id):
    """change a user's password"""
    # Retrieve user from db by user_id
    user = User.query.get(user_id)
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
