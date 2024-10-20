from uuid import uuid4
from flask import Blueprint, request, jsonify
from api import db
from api.auth import role_required
from api.models.comment import Comment
from api.models.picture import Picture
import os
from werkzeug.utils import secure_filename
from api.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """checks if a file type is allowed"""
    return '.' and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Create a bp for picture-related routes
picture_bp = Blueprint('picture_bp', __name__)


@picture_bp.route('/pictures/upload', methods=['POST'])
@jwt_required()
def upload_picture():
    """Upload a new picture with a dynamic description."""
    current_user_id = get_jwt_identity()
    # Check if the current user exists
    user = User.query.get(current_user_id)
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

        new_picture = Picture(user_id=current_user_id, image_url=file_path, description=description)
        db.session.add(new_picture)
        db.session.commit()

        return jsonify({
            "message": "Picture uploaded successfully!",
            "picture": {
                "id": new_picture.id,
                "user_id": new_picture.user_id,
                "image_url": file_path,
                "description": new_picture.description,
                "created_at": new_picture.created_at,
                "updated_at": new_picture.updated_at
            }
        }), 201

    return jsonify({"error": "File type not allowed"}), 400


@picture_bp.route('/pictures/<int:picture_id>', methods=['GET'], endpoint='get_picture_by_id')
@jwt_required()
def get_picture_by_id(picture_id):
    """retrieve a picture by its id"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    return jsonify({
        "id": picture.id,
        "user_id": picture.user_id,
        "image_url": picture.image_url,
        "description": picture.description,
        "created_at": picture.created_at,
        "updated_at": picture.updated_at
    }), 200


@picture_bp.route('/user/pictures', methods=['GET'], endpoint='get_user_pictures')
@jwt_required()
def get_user_pictures():
    """retrieve all pictures of a particular user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_pictures = Picture.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        "id": picture.id,
        "user_id": picture.user_id,
        "image_url": picture.image_url,
        "description": picture.description,
        "created_at": picture.created_at,
        "updated_at": picture.updated_at
        } for picture in user_pictures
    ]), 200


@picture_bp.route('/pictures/<int:picture_id>', methods=['PUT'], endpoint='update_picture')
@jwt_required()
def update_picture(picture_id):
    """update picture metadata (like description)"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    # get user_id from jwt token
    current_user_id = get_jwt_identity()
    # check if current user is the owner of the picture
    if picture.user_id != current_user_id:
        return jsonify({"error": "You are not allowed to update this picture"}), 403

    description = request.form.get('description')
    if description:
        picture.description = description

    db.session.commit()
    db.session.refresh(picture)

    return jsonify({
        "message": "Picture updated successfully",
        "picture": {
            "id": picture.id,
            "user_id": picture.user_id,
            "image_url": picture.image_url,
            "description": picture.description,
            "created_at": picture.created_at,
            "updated_at": picture.updated_at
        }
        }), 200


@picture_bp.route('/pictures/<int:picture_id>', methods=['DELETE'], endpoint='delete_picture')
@jwt_required()
def delete_picture(picture_id):
    """Delete a specific picture"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    # get user_id from jwt token
    current_user_id = get_jwt_identity()
    # check if current user is the owner of the picture
    if picture.user_id != current_user_id:
        return jsonify({"error": "You are not allowed to delete this picture"}), 403

    # Delete the picture from the file system
    if os.path.exists(picture.image_url):
        os.remove(picture.image_url)

    # Delete the image_url entry from db
    db.session.delete(picture)
    db.session.commit()

    return jsonify({"message": "Picture deleted successfully!"}), 200


# Search pictures by description
@picture_bp.route('/pictures/search', methods=['GET'])
@jwt_required()
def search_pictures():
    """search for pictures by description"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Search query is required"}), 400

    pictures = Picture.query.filter(Picture.description.ilike(f"%{query}%")).all()

    pictures_list = [{
        "id": picture.id,
        "user_id": picture.user_id,
        "image_url": picture.image_url,
        "description": picture.description,
        "created_at": picture.created_at,
        "updated_at": picture.updated_at,
    } for picture in pictures]

    return jsonify(pictures_list), 200
