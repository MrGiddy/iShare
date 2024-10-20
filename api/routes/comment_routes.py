#!/usr/bin/env python3
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from api.auth import role_required
from api.models.picture import Picture
from api.models.user import User
from api.models.comment import Comment
from api import db


# Create a bp for comment-related routes
comment_bp = Blueprint('comment_bp', __name__)


# POST: Add a comment to a specific picture
@comment_bp.route('/pictures/<int:picture_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(picture_id):
    """add a comment to a picture"""
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')

    if not content:
        return jsonify({"error": "Comment content is required"}), 400

    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_comment = Comment(user_id=user_id, picture_id=picture_id, content=content)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added successfully",
        "comment": {
            "id": new_comment.id,
            "user_id": new_comment.user_id,
            "picture_id": new_comment.picture_id,
            "content": new_comment.content,
            "created_at": new_comment.created_at,
            "updated_at": new_comment.updated_at
        }
    }), 201


# GET: Retrieve all comments for a specific picture
@comment_bp.route('/pictures/<int:picture_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(picture_id):
    """retrieves all comments for a specific picture"""
    picture = Picture.query.get(picture_id)
    if not picture:
        return jsonify({"error": "Picture not found"}), 404

    comments = Comment.query.filter_by(picture_id=picture_id).all()
    comments_list = [{
        "id": comment.id,
        "user_id": comment.user_id,
        "picture_id": comment.picture_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    } for comment in comments]

    return jsonify(comments_list), 200


# GET: Retrieve a comment by it's id
@comment_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment(comment_id):
    """retrieve a comment by it's id"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    return jsonify({
        "id": comment.id,
        "user_id": comment.user_id,
        "picture_id": comment.picture_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    }), 200


# PUT: Update a specific comment
@comment_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """update a specific comment"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"})

    # Only proceed to update if the current user owns the comment
    current_user_id = get_jwt_identity()
    if current_user_id != comment.user_id:
        return jsonify({"error": "You are not allowed to update this comment"}), 403

    data = request.get_json()
    new_content = data.get('content')

    if not new_content:
        return jsonify({"error": "Comment content is required"}), 400

    comment.content = new_content
    db.session.commit()
    db.session.refresh(comment)

    return jsonify({
        "message": "Comment updated successfully!",
        "comment": {
            "id": comment.id,
            "user_id": comment.user_id,
            "picture_id": comment.picture_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        }
    }), 200


# DELETE: Delete a specific comment
@comment_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    "delete a specific comment"
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    # Only proceed to delete if the current user owns the comment
    current_user_id = get_jwt_identity()
    if current_user_id != comment.user_id:
        return jsonify({"error": "You are not allowed to delete this comment"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully!"}), 200
