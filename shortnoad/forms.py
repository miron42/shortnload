"""Формы Flask-WTF для пользовательского ввода."""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from shortnoad.constants import (
    CUSTOM_ID_PATTERN,
    MAX_CUSTOM_ID_LENGTH,
    MIN_CUSTOM_ID_LENGTH
)


class ShortenForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Поле обязательно для заполнения.'),
            URL(message='Введите корректную ссылку.')
        ]
    )

    custom_id = StringField(
        'Ваш вариант короткой ссылки (необязательно)',
        validators=[
            Length(
                min=MIN_CUSTOM_ID_LENGTH,
                max=MAX_CUSTOM_ID_LENGTH,
                message=(
                    'От {min_len} до {max_len} символов.'.format(
                        min_len=MIN_CUSTOM_ID_LENGTH,
                        max_len=MAX_CUSTOM_ID_LENGTH
                    )
                )
            ),
            Regexp(
                CUSTOM_ID_PATTERN,
                message='Только латинские буквы и цифры.'
            ),
            Optional()
        ]
    )
