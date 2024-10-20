from api import db
from datetime import datetime, timezone


class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(40), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'
