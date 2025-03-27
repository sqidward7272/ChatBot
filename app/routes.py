from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User

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
            return redirect(url_for("main.dashboard"))
        flash("Неверные данные для входа", "danger")
    return render_template("login.html")

@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))
