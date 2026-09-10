from functools import wraps

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from forms import DoctorForm
from models import Admin, Appointment, Doctor, Patient

admin_bp = Blueprint("admin", __name__)


def admin_only(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            return redirect(url_for("main.dashboard"))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.get("/dashboard")
@admin_only
def dashboard():
    return render_template("admin_dashboard.html", doctors=Doctor.query.order_by(Doctor.full_name).all(), patients=Patient.query.order_by(Patient.full_name).all(), appointments=Appointment.query.order_by(Appointment.created_at.desc()).all())


@admin_bp.route("/doctors/new", methods=["GET", "POST"])
@admin_only
def add_doctor():
    form = DoctorForm()
    if form.validate_on_submit():
        if Doctor.query.filter((Doctor.email == form.email.data.lower()) | (Doctor.license_number == form.license_number.data)).first():
            flash("Email or license number is already in use.", "warning")
        else:
            doctor = Doctor(full_name=form.full_name.data, email=form.email.data.lower(), specialty=form.specialty.data, license_number=form.license_number.data, phone=form.phone.data, bio=form.bio.data)
            doctor.set_password(form.password.data or "ChangeMe123!")
            db.session.add(doctor)
            db.session.commit()
            flash("Doctor added successfully.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin_dashboard.html", form=form, doctors=Doctor.query.all(), patients=Patient.query.all(), appointments=Appointment.query.all())


@admin_bp.route("/doctors/<int:doctor_id>/edit", methods=["GET", "POST"])
@admin_only
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    if form.validate_on_submit():
        form.populate_obj(doctor)
        doctor.email = form.email.data.lower()
        if form.password.data:
            doctor.set_password(form.password.data)
        db.session.commit()
        flash("Doctor profile updated.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin_dashboard.html", form=form, editing=doctor, doctors=Doctor.query.all(), patients=Patient.query.all(), appointments=Appointment.query.all())


@admin_bp.post("/doctors/<int:doctor_id>/delete")
@admin_only
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False
    db.session.commit()
    flash("Doctor deactivated.", "success")
    return redirect(url_for("admin.dashboard"))
