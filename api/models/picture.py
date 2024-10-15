from api import db


class Picture(db.Model):
    __tablename__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='pictures', lazy=True)
    comments = db.relationship('Comment', back_populates='picture', lazy=True, cascade='all, delete-orphan')
