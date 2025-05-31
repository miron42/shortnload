import random
import string

from yacut.models import URLMap

# Символы, используемые для генерации коротких ссылок
CHARS = string.ascii_letters + string.digits  # A-Z, a-z, 0-9


def get_unique_short_id(length=6):
    """Генерирует уникальный короткий идентификатор заданной длины.

    Проверяет, чтобы идентификатор не был уже занят в базе данных.

    Args:
        length (int): Длина идентификатора (по умолчанию 6).

    Returns:
        str: Уникальный короткий идентификатор.
    """
    while True:
        short_id = ''.join(random.choices(CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
