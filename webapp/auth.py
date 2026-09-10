from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from extensions import db
from forms import LoginForm, RegistrationForm
from models import Admin, Doctor, Patient, user_identity

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if Patient.query.filter_by(email=form.email.data.lower()).first():
            flash("An account with this email already exists.", "warning")
        else:
            patient = Patient(full_name=form.full_name.data, email=form.email.data.lower(), phone=form.phone.data, date_of_birth=form.date_of_birth.data)
            patient.set_password(form.password.data)
            db.session.add(patient)
            db.session.commit()
            flash("Your account is ready. Please sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        model = {"patient": Patient, "doctor": Doctor, "admin": Admin}[form.role.data]
        user = model.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data) and getattr(user, "is_active", True):
            login_user(user, remember=form.remember.data == "yes")
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        flash("Invalid credentials or inactive account.", "danger")
    return render_template("login.html", form=form)


@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
