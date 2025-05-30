import random
import string

from yacut.models import URLMap

CHARS = string.ascii_letters + string.digits  # A-Z, a-z, 0-9


def get_unique_short_id(length=6):
    while True:
        short_id = ''.join(random.choices(CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
