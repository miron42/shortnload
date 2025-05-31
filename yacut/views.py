import os
import urllib
from flask import Blueprint, render_template, redirect, url_for, request
import aiohttp
from yacut.forms import ShortenForm
from yacut.models import URLMap
from yacut import db
from yacut.utils import get_unique_short_id

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index_view():
    form = ShortenForm()
    error = None
    short_url = None

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data or get_unique_short_id()

        existing = URLMap.query.filter_by(short=custom_id).first()
        if custom_id.lower() == 'files' or existing:
            error = 'Предложенный вариант короткой ссылки уже существует.'
        else:
            new_entry = URLMap(original=original_link, short=custom_id)
            db.session.add(new_entry)
            db.session.commit()
            short_url = url_for('main.redirect_view',
                                short=custom_id, _external=True)

    return render_template(
        'index.html',
        form=form,
        error=error,
        short_url=short_url
    ), 200


@bp.route('/<string:short>')
def redirect_view(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)


def get_yd_headers():
    token = os.environ.get('DISK_TOKEN')
    return {'Authorization': f'OAuth {token}'}


def get_yd_urls():
    host = os.environ.get(
        'YANDEX_API_HOST', 'https://cloud-api.yandex.net').rstrip('/')
    version = 'v1'
    upload_url = f'{host}/{version}/disk/resources/upload'
    download_url = f'{host}/{version}/disk/resources/download'
    return upload_url, download_url


@bp.route('/files', methods=['GET', 'POST'])
async def files_view():

    if request.method == 'GET':
        return render_template('files.html')

    UPLOAD_URL, DOWNLOAD_URL = get_yd_urls()

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
            resp1 = await session.get(UPLOAD_URL, params=params_upload)
            resp1.raise_for_status()
            data1 = await resp1.json()
            upload_href = data1.get('href')

            file_bytes = f.read()
            put_resp = await session.put(upload_href, data=file_bytes)
            put_resp.raise_for_status()

            raw_location = put_resp.headers.get(
                'Location', '')  # например "/disk/app/имя.png"
            file_on_disk = urllib.parse.unquote(raw_location).lstrip('/disk')

            params_download = {'path': file_on_disk}
            resp2 = await session.get(DOWNLOAD_URL, params=params_download)
            resp2.raise_for_status()
            data2 = await resp2.json()
            direct_href = data2.get('href')

            short = get_unique_short_id()
            while URLMap.query.filter_by(short=short).first():
                short = get_unique_short_id()

            new_entry = URLMap(original=direct_href, short=short)
            db.session.add(new_entry)
            db.session.commit()

            short_link = url_for('main.redirect_view',
                                 short=short, _external=True)

            results.append((filename, short_link))

    return render_template('files.html', files=results)
