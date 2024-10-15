from uuid import uuid4
from flask import Blueprint, request, jsonify
from api import db
from api.models.picture import Picture
import os
from werkzeug.utils import secure_filename

from api.models.user import User


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """checks if a file type is allowed"""
    return '.' and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create a bp for picture-related routes
picture_bp = Blueprint('picture_bp', __name__)


@picture_bp.route('/upload/<int:user_id>', methods=['POST'])
def upload_picture(user_id):
    """Upload a new picture with a dynamic description."""
    # Check if the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    description = request.form.get('description')  # Get description from form data

    if not description:
        return jsonify({"error": "Description is required"}), 400

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Check if the file is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # Create an entry in the database with
        # a unique file path and dynamic description
        new_picture = Picture(user_id=user_id, image_url=file_path, description=description)
        db.session.add(new_picture)
        db.session.commit()

        return jsonify({"message": "Picture uploaded successfully!", "image_url": file_path}), 201

    return jsonify({"error": "File type not allowed"}), 400


@picture_bp.route('/pictures/<int:picture_id>', methods=['GET'], endpoint='get_picture')
def get_picture(picture_id):
    """retrieve a picture by its id"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    return jsonify({
        "id": picture.id,
        "user_id": picture.user_id,
        "image_url": picture.image_url,
        "description": picture.description
    }), 200


@picture_bp.route('/pictures', methods=['GET'])
def get_all_pictures():
    """retrieve all pictures across all users"""
    pictures = Picture.query.all()
    return jsonify([
        {
            "id": picture.id,
            "user_id": picture.user_id,
            "image_url": picture.image_url,
            "description": picture.description
        } for picture in pictures
    ]), 200


@picture_bp.route('/users/<int:user_id>/pictures', methods=['GET'], endpoint='get_user_pictures')
def get_user_pictures(user_id):
    """retrieve all pictures of a particular user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_pictures = Picture.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": picture.id,
        "user_id": picture.user_id,
        "image_url": picture.image_url,
        "description": picture.description
        } for picture in user_pictures
    ]), 200


@picture_bp.route('/pictures/<int:picture_id>', methods=['PUT'], endpoint='update_picture')
def update_picture(picture_id):
    """update picture metadata (like description)"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    description = request.form.get('description')
    if description:
        picture.description = description

    db.session.commit()

    print(picture.description)
    return jsonify({"message": "Picture updated successfully"}), 200


@picture_bp.route('/pictures/<int:picture_id>', methods=['DELETE'], endpoint='delete_picture')
def delete_picture(picture_id):
    """Delete a specific picture"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    # Delete the picture from the file system
    if os.path.exists(picture.image_url):
        os.remove(picture.image_url)

    # Delete the image_url entry from db
    db.session.delete(picture)
    db.session.commit()

    return jsonify({"message": "Picture deleted successfully!"}), 200
