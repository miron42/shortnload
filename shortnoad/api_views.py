import re
from http import HTTPStatus

from flask import jsonify, request

from shortnoad import app
from shortnoad.models import URLMap
from shortnoad.error_handlers import InvalidAPIUsage
from shortnoad.constants import (
    CUSTOM_ID_PATTERN,
    RESERVED_NAMES,
    MAX_CUSTOM_ID_LENGTH,
    MIN_CUSTOM_ID_LENGTH
)


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """Создаёт короткую ссылку по переданному URL и custom_id."""
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса',
                              HTTPStatus.BAD_REQUEST)

    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!', HTTPStatus.BAD_REQUEST)

    if custom_id and len(custom_id) > 0 and (
        not MIN_CUSTOM_ID_LENGTH <= len(custom_id) <= MAX_CUSTOM_ID_LENGTH
        or custom_id.lower() in RESERVED_NAMES
        or not re.fullmatch(CUSTOM_ID_PATTERN, custom_id)
    ):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )

    new_link = URLMap.create(original=url, short=custom_id)
    return jsonify(new_link.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    """Получает оригинальный URL по его короткой версии."""
    url_map = URLMap.get_by_short(short_id)
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
