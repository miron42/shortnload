from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Создание и конфигурация приложения
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI', 'sqlite:///db.sqlite3')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'S3CR3T-K3Y-F0R-Y4CUT')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

# Инициализация расширений
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

# Импорт и регистрация представлений и обработчиков ошибок
from . import views, api_views, error_handlers
