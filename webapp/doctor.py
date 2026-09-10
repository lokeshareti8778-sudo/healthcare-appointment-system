from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_

from extensions import db
from forms import PrescriptionForm, StatusForm
from models import Appointment, AppointmentStatus, Prescription

doctor_bp = Blueprint("doctor", __name__)


def doctor_required():
    return current_user.is_authenticated and current_user.role == "doctor"


@doctor_bp.get("/appointments")
@login_required
def appointments():
    if not doctor_required():
        return redirect(url_for("main.dashboard"))
    records = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time).all()
    return render_template("appointments.html", appointments=records, doctor_view=True)


@doctor_bp.post("/appointments/<int:appointment_id>/status")
@login_required
def update_status(appointment_id):
    if not doctor_required():
        return redirect(url_for("main.dashboard"))
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.id).first_or_404()
    form = StatusForm()
    if form.validate_on_submit():
        appointment.status = form.status.data
        db.session.commit()
        flash("Appointment status updated.", "success")
    return redirect(url_for("doctor.appointments"))


@doctor_bp.route("/appointments/<int:appointment_id>/prescription", methods=["GET", "POST"])
@login_required
def add_prescription(appointment_id):
    if not doctor_required():
        return redirect(url_for("main.dashboard"))
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.id).first_or_404()
    form = PrescriptionForm(obj=appointment.prescription)
    if form.validate_on_submit():
        prescription = appointment.prescription or Prescription(appointment_id=appointment.id, doctor_id=current_user.id)
        prescription.medicines = form.medicines.data
        prescription.instructions = form.instructions.data
        db.session.add(prescription)
        appointment.status = AppointmentStatus.COMPLETED.value
        db.session.commit()
        flash("Prescription saved.", "success")
        return redirect(url_for("doctor.appointments"))
    return render_template("prescription.html", form=form, appointment=appointment)
