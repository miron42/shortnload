import random
from datetime import datetime
from http import HTTPStatus

from flask import url_for

from shortnoad import db
from shortnoad.constants import (
    CHARS,
    DEFAULT_SHORT_ID_LENGTH,
    FILES_ROUTE,
    MAX_CUSTOM_ID_LENGTH,
    MAX_URL_LENGTH
)
from shortnoad.error_handlers import InvalidAPIUsage


class URLMap(db.Model):
    """Модель для хранения сопоставления оригинального и короткого URL."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(db.String(MAX_CUSTOM_ID_LENGTH),
                      unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<URLMap short='{self.short}' original='{self.original}'>"

    def to_dict(self):
        """Преобразует объект в словарь для API-ответа."""
        return {
            'url': self.original,
            'short_link': url_for(
                'redirect_view',
                short=self.short,
                _external=True
            )
        }

    @staticmethod
    def get_by_short(short_id):
        """Возвращает объект по короткому ID или None."""
        return URLMap.query.filter_by(short=short_id).first()

    @staticmethod
    def create(original: str, short: str = None) -> "URLMap":
        """Создаёт и сохраняет URLMap. Проверяет имена."""
        if short:
            if short.lower() == FILES_ROUTE.strip('/'):
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.',
                    HTTPStatus.BAD_REQUEST
                )
            if URLMap.get_by_short(short):
                raise InvalidAPIUsage(
                    'Предложенный вариант короткой ссылки уже существует.',
                    HTTPStatus.BAD_REQUEST
                )
        else:
            short = URLMap.generate_unique_short_id()

        new_link = URLMap(original=original, short=short)
        db.session.add(new_link)
        db.session.commit()
        return new_link

    @staticmethod
    def generate_unique_short_id(length=DEFAULT_SHORT_ID_LENGTH) -> str:
        """Генерирует уникальный короткий идентификатор заданной длины."""
        while True:
            short_id = ''.join(random.choices(CHARS, k=length))
            if not URLMap.query.filter_by(short=short_id).first():
                return short_id
