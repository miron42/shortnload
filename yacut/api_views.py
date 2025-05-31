from flask import Blueprint, jsonify, request, url_for
from yacut.models import URLMap
from yacut.utils import get_unique_short_id
from yacut import db
import re

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/id/', methods=['POST'])
def create_short_link():
    if not request.is_json:
        return jsonify(message='Отсутствует тело запроса'), 400

    try:
        data = request.get_json()
    except Exception:
        return jsonify(message='Отсутствует тело запроса'), 400

    if not data:
        return jsonify(message='Отсутствует тело запроса'), 400

    url = data.get('url')
    custom_id = data.get('custom_id')

    if not url:
        return jsonify(message='"url" является обязательным полем!'), 400

    # если без custom_id и URL уже есть
    existing_by_url = URLMap.query.filter_by(original=url).first()
    if not custom_id and existing_by_url:
        return (
            jsonify(
                short_link=url_for('main.redirect_view',
                                   short=existing_by_url.short,
                                   _external=True),
                message='Короткая ссылка для переданного URL уже существует.'
            ),
            409
        )

    if custom_id:
        # длиннее 16 → та же ошибка, что и для недопустимого имени
        if len(custom_id) > 16:
            return jsonify(
                message='Указано недопустимое имя для короткой ссылки'), 400

        if not re.fullmatch(r'[a-zA-Z0-9]+', custom_id):
            return jsonify(
                message='Указано недопустимое имя для короткой ссылки'), 400

        existing_by_short = URLMap.query.filter_by(short=custom_id).first()
        if custom_id.lower() == 'files' or existing_by_short:
            return jsonify(message=(
                'Предложенный вариант короткой ссылки '
                'уже существует.'
            )), 400

        short = custom_id
    else:
        short = get_unique_short_id()

    new_link = URLMap(original=url, short=short)
    db.session.add(new_link)
    db.session.commit()

    short_link = url_for('main.redirect_view', short=short, _external=True)
    return jsonify(url=url, short_link=short_link), 201


@bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    print('DEBUG: DB contains →', [url.short for url in URLMap.query.all()])
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify(message='Указанный id не найден'), 404
    return jsonify(url=url_map.original), 200
