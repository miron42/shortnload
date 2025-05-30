from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL


class ShortenForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message="Поле обязательно для заполнения."),
            URL(message="Введите корректную ссылку.")
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки (необязательно)',
        validators=[
            Length(max=16, message="Не больше 16 символов."),
            Regexp(r'^[a-zA-Z0-9]*$',
                   message="Только латинские буквы и цифры."),
            Optional()
        ]
    )
