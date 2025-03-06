import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost:5432/plagiarism"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "1234"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ----- Модель пользователя -----
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

# ----- Модель проверок плагиата -----
class PlagiarismCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    plagiarism_score = db.Column(db.Float, nullable=False)
    checked_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# ----- Загрузка пользователя -----
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----- Главная страница -----
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# ----- Регистрация -----
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Этот email уже зарегистрирован!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Вы успешно зарегистрировались! Теперь войдите в систему.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ----- Вход -----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Вы вошли в систему!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Неверный email или пароль", "danger")

    return render_template("login.html")

# ----- Выход -----
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("login"))

# ----- Личный кабинет -----
@app.route("/dashboard")
@login_required
def dashboard():
    checks = PlagiarismCheck.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", user=current_user, checks=checks)

# ----- Страница проверки текста -----
@app.route("/check_page", methods=["GET"])
@login_required
def check_page():
    return render_template("check.html")

# ----- Проверка плагиата -----
@app.route("/check", methods=["POST"])
@login_required
def check_plagiarism():
    text = request.form["text"]
    
    if not text.strip():
        flash("Введите текст для проверки!", "danger")
        return redirect(url_for("check_page"))
    
    try:
        # Запрос к DeepSeek через OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek/deepseek-r1",
            "messages": [{"role": "user", "content": f"Определи процент уникальности следующего текста: {text}"}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"].strip()
            
            if "100%" in result or "уникальный" in result.lower():
                plagiarism_score = 100.0
            elif "0%" in result or "не уникальный" in result.lower():
                plagiarism_score = 0.0
            else:
                plagiarism_score = 50.0  # По умолчанию

            # Сохранение результата в БД
            check = PlagiarismCheck(user_id=current_user.id, text=text, plagiarism_score=plagiarism_score)
            db.session.add(check)
            db.session.commit()

            flash(f"Проверка завершена! Процент уникальности: {plagiarism_score}%", "info")
            return redirect(url_for("dashboard"))
        else:
            flash(f"Ошибка API: {response.status_code} - {response.text}", "danger")
            return redirect(url_for("check_page"))

    except Exception as e:
        flash(f"Ошибка при запросе к DeepSeek: {str(e)}", "danger")
        return redirect(url_for("check_page"))

# ----- Запуск -----
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)