from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, PlagiarismCheck

main = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Вы успешно вошли!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Неверные данные для входа", "danger")
    return render_template("login.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Проверяем, нет ли такого email
        if User.query.filter_by(email=email).first():
            flash("Этот email уже зарегистрирован", "danger")
            return redirect(url_for("main.register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Вы успешно зарегистрировались! Теперь войдите.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@main.route("/check", methods=["GET", "POST"])
@login_required
def check_page():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if not text:
            flash("Введите текст для проверки!", "danger")
            return redirect(url_for("main.check_page"))

        # Здесь можно вызвать реальную проверку плагиата
        # Пока ставим заглушку:
        plagiarism_score = 95.0

        new_check = PlagiarismCheck(
            user_id=current_user.id,
            text=text,
            plagiarism_score=plagiarism_score
        )
        db.session.add(new_check)
        db.session.commit()

        flash(f"Проверка завершена! Процент уникальности: {plagiarism_score}%", "info")
        return redirect(url_for("main.dashboard"))

    return render_template("check.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.login"))
