#!/usr/bin/env python3
from flask import Blueprint, request, jsonify
from api import db, bcrypt
from api.models.user import User


# Create a Blueprint for user-related routes
user_bp = Blueprint('user_bp', __name__)


# Registration route
@user_bp.route('/register', methods=['POST'])
def register():
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
