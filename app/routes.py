import requests
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Пользователь с таким email уже существует!")
            return redirect(url_for('main.register'))

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна! Войдите в систему.")
        return redirect(url_for('main.login'))
    return render_template("register.html")

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            flash("Вы вошли в систему.")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Неверный email или пароль.")
            return redirect(url_for('main.login'))
    return render_template("login.html")

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.")
    return redirect(url_for('main.index'))

@main.route('/check', methods=['GET', 'POST'])
@login_required
def check():
    result = None
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if not text:
            flash("Введите текст для проверки!")
        else:
            try:
                url = "https://ai-content-detector-ai-gpt.p.rapidapi.com/api/detectText/"
                headers = {
                    "Content-Type": "application/json",
                    "X-RapidAPI-Key": "ba5432c13fmsh68f6bf1d65e30f1p11d6fejsn90b9e8518056",
                    "X-RapidAPI-Host": "ai-content-detector-ai-gpt.p.rapidapi.com"
                }
                payload = {"text": text}

                response = requests.post(url, json=payload, headers=headers)

                print("DEBUG STATUS:", response.status_code)
                print("DEBUG BODY:", response.text)

                if response.status_code != 200:
                    result = f"❌ Ошибка: API вернул код {response.status_code}."
                else:
                    data = response.json()
                    status = data.get("status", False)
                    fake_percentage = data.get("fakePercentage", 0)
                    is_human = data.get("isHuman", 0)

                    if not status:
                        result = "❌ Ошибка: API не вернул успешный ответ."
                    elif fake_percentage == 0 and is_human == 0:
                        result = "⚠️ Невозможно определить. Попробуйте длиннее текст."
                    else:
                        label = "🤖 AI" if is_human == 0 else "🧑 Человек"
                        result = f"{label} — AI вероятность: {fake_percentage:.1f}%"

                    flash("Проверка завершена!")

            except Exception as e:
                result = f"Ошибка при проверке: {str(e)}"
                flash("Произошла ошибка при обращении к AI Content Detector.")

    return render_template("check.html", result=result)
