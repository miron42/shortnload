from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 'sqlite:///db.sqlite3')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'S3CR3T-K3Y-F0R-Y4CUT')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from . import views, api_views
    app.register_blueprint(views.bp)
    app.register_blueprint(api_views.bp)

    return app


app = create_app()
