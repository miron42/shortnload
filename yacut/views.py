from flask import Blueprint, render_template, flash, redirect, url_for
from yacut.forms import ShortenForm
from yacut.models import URLMap
from yacut import db
from yacut.utils import get_unique_short_id

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index_view():
    form = ShortenForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom = form.custom_id.data

        if custom:
            if custom == 'files' or URLMap.query.filter_by(short=custom).first():
                flash('Предложенный вариант короткой ссылки уже существует.', 'error')
                return render_template('index.html', form=form)
            short = custom
        else:
            short = get_unique_short_id()

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()

        short_url = url_for('main.redirect_view', short=short, _external=True)
        return render_template('index.html', form=form, short_url=short_url)

    return render_template('index.html', form=form)


@bp.route('/<string:short>')
def redirect_view(short):
    url_map = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map.original)
