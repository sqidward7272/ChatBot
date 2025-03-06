from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost:5432/plagiarism"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Проверяем подключение
with app.app_context():
    try:
        db.engine.connect()
        print("✅ Подключение к базе данных успешно!")
    except Exception as e:
        print("❌ Ошибка подключения:", e)
