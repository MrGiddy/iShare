from api import db
from sqlalchemy.sql import func


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='comments', lazy=True)
    picture = db.relationship('Picture', back_populates='comments', lazy=True)
