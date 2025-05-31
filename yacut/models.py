from datetime import datetime
from . import db


class URLMap(db.Model):
    """Модель для хранения сопоставления оригинального и короткого URL."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<URLMap short='{self.short}' original='{self.original}'>"
