from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # Загружаем конфигурацию из config.py

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Указываем, куда перенаправлять при попытке доступа без авторизации
    login_manager.login_view = "main.login"

    # Подключаем Blueprint с маршрутами
    from app.routes import main
    app.register_blueprint(main)

    return app
