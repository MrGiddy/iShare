from api import db
from sqlalchemy.sql import func


class Picture(db.Model):
    __tablename__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    user = db.relationship('User', back_populates='pictures', lazy=True)
    comments = db.relationship('Comment', back_populates='picture', lazy=True, cascade='all, delete-orphan')
