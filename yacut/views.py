import os
import urllib

import aiohttp
from flask import redirect, render_template, request

from yacut import app
from yacut.constants import FILES_ROUTE
from yacut.forms import ShortenForm
from yacut.models import URLMap


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Главная страница. Обрабатывает форму сокращения ссылки."""
    form = ShortenForm()

    if not form.validate_on_submit():
        return render_template(
            'index.html',
            form=form,
            error=None,
            short_url=None
        )

    original_link = form.original_link.data
    custom_id = form.custom_id.data or URLMap.generate_unique_short_id()

    if custom_id.lower() == FILES_ROUTE.strip('/') or \
            URLMap.get_by_short(custom_id):
        error = 'Предложенный вариант короткой ссылки уже существует.'
        return render_template(
            'index.html',
            form=form,
            error=error,
            short_url=None
        )

    new_entry = URLMap.create(original=original_link, short=custom_id)
    short_url = new_entry.to_dict()['short_link']
    return render_template(
        'index.html',
        form=form,
        error=None,
        short_url=short_url
    )


@app.route('/<string:short>')
def redirect_view(short):
    """Перенаправляет по короткой ссылке на оригинальный URL."""
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


def get_yd_headers():
    """Возвращает заголовки авторизации для Яндекс.Диска."""
    token = os.environ.get('DISK_TOKEN')
    return {'Authorization': f'OAuth {token}'}


def get_yd_urls():
    """Генерирует ссылки для загрузки и скачивания с Яндекс.Диска."""
    host = os.environ.get(
        'YANDEX_API_HOST', 'https://cloud-api.yandex.net'
    ).rstrip('/')
    version = 'v1'
    upload_url = f'{host}/{version}/disk/resources/upload'
    download_url = f'{host}/{version}/disk/resources/download'
    return upload_url, download_url


@app.route(FILES_ROUTE, methods=['GET', 'POST'])
async def files_view():
    """Обрабатывает загрузку файлов на Яндекс.Диск и выдаёт короткие ссылки."""
    if request.method == 'GET':
        return render_template('files.html')

    upload_url, download_url = get_yd_urls()
    uploaded_files = request.files.getlist('files')
    results = []

    yd_headers = get_yd_headers()
    async with aiohttp.ClientSession(headers=yd_headers) as session:
        for f in uploaded_files:
            filename = f.filename
            params_upload = {
                'path': f'app:/{filename}',
                'overwrite': 'false',
            }
            resp1 = await session.get(upload_url, params=params_upload)
            resp1.raise_for_status()
            data1 = await resp1.json()
            upload_href = data1.get('href')

            file_bytes = f.read()
            put_resp = await session.put(upload_href, data=file_bytes)
            put_resp.raise_for_status()

            raw_location = put_resp.headers.get('Location', '')
            file_on_disk = urllib.parse.unquote(raw_location).lstrip('/disk')

            params_download = {'path': file_on_disk}
            resp2 = await session.get(download_url, params=params_download)
            resp2.raise_for_status()
            data2 = await resp2.json()
            direct_href = data2.get('href')

            short = URLMap.generate_unique_short_id()
            new_entry = URLMap.create(original=direct_href, short=short)
            short_link = new_entry.to_dict()['short_link']
            results.append((filename, short_link))

    return render_template('files.html', files=results)
