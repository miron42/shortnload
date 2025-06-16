import string

# Длина короткого идентификатора по умолчанию
DEFAULT_SHORT_ID_LENGTH = 6

# Максимальная длина оригинальной ссылки
MAX_URL_LENGTH = 2048

# Максимальная длина пользовательского идентификатора
MAX_CUSTOM_ID_LENGTH = 16

# Минимальная длина пользовательского идентификатора
MIN_CUSTOM_ID_LENGTH = 1

# Разрешённые символы для генерации коротких ссылок
CHARS = string.ascii_letters + string.digits

# Паттерн для проверки пользовательского идентификатора
CUSTOM_ID_PATTERN = r'^[a-zA-Z0-9]+$'

# Зарезервированные имена, которые нельзя использовать для коротких ссылок
RESERVED_NAMES = {'files'}

# Константы для работы с Яндекс.Диском
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
FILES_ROUTE = '/files'
