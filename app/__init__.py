from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config') # Загружаем настройки из config.py

    db.init_app(app)
    login_manager.init_app(app)

    # Если маршрут входа в blueprints "main"
    login_manager.login_view = "main.login"

    from app.routes import main  # Импортируем blueprints
    app.register_blueprint(main)

    return app
