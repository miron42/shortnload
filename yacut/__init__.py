from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Инициализация расширений Flask

# Работа с базой данных
db = SQLAlchemy()
# Защита от CSRF-атак (для форм)
csrf = CSRFProtect()
# Миграции базы данных
migrate = Migrate()


def create_app():
    """Фабрика приложения Flask.

    Настраивает конфигурацию, расширения и регистрирует blueprints.
    """
    load_dotenv()

    app = Flask(__name__)

    # Конфигурация приложения
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 'sqlite:///db.sqlite3')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'S3CR3T-K3Y-F0R-Y4CUT')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False  # Можно включить в продакшне

    # Инициализация расширений
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Регистрация blueprints
    from . import views, api_views
    app.register_blueprint(views.bp)
    app.register_blueprint(api_views.bp)

    @app.errorhandler(404)
    def page_not_found(e):
        """Обработчик ошибки 404 (страница не найдена)."""
        return render_template('404.html'), 404

    return app


# Создание экземпляра приложения
app = create_app()
