from datetime import date

import requests
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from forms import AppointmentForm
from models import Appointment, Doctor

appointment_bp = Blueprint("appointment", __name__)


def get_function_appointment_data():
    url = current_app.config["AZURE_FUNCTION_URL"]
    if not url:
        raise RuntimeError("AZURE_FUNCTION_URL is not configured")
    headers = {"x-functions-key": current_app.config["AZURE_FUNCTION_KEY"]} if current_app.config["AZURE_FUNCTION_KEY"] else {}
    response = requests.post(url, json={"fee": current_app.config["APPOINTMENT_FEE"]}, headers=headers, timeout=8)
    response.raise_for_status()
    data = response.json()
    if not {"appointmentId", "token", "fee", "status"}.issubset(data):
        raise ValueError("Azure Function returned an incomplete appointment response")
    return data


@appointment_bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    if current_user.role != "patient":
        flash("Only patients can book appointments.", "warning")
        return redirect(url_for("main.dashboard"))
    form = AppointmentForm()
    form.doctor_id.choices = [(doctor.id, f"Dr. {doctor.full_name} - {doctor.specialty}") for doctor in Doctor.query.filter_by(is_active=True).order_by(Doctor.full_name).all()]
    if form.validate_on_submit():
        if form.appointment_date.data < date.today():
            flash("Appointments must be scheduled for today or later.", "warning")
        elif Appointment.query.filter_by(doctor_id=form.doctor_id.data, appointment_date=form.appointment_date.data, appointment_time=form.appointment_time.data).first():
            flash("That time is already booked. Please choose another slot.", "warning")
        else:
            try:
                details = get_function_appointment_data()
            except (requests.RequestException, ValueError, RuntimeError) as error:
                current_app.logger.exception("Appointment ID service failed: %s", error)
                flash("The appointment service is temporarily unavailable. Please try again.", "danger")
            else:
                appointment = Appointment(appointment_id=details["appointmentId"], queue_token=details["token"], fee=details["fee"], status=details["status"], patient_id=current_user.id, doctor_id=form.doctor_id.data, appointment_date=form.appointment_date.data, appointment_time=form.appointment_time.data, reason=form.reason.data)
                db.session.add(appointment)
                db.session.commit()
                flash(f"Appointment confirmed. Your queue token is {appointment.queue_token}.", "success")
                return redirect(url_for("main.appointment_history"))
    return render_template("appointments.html", form=form, appointments=[])


@appointment_bp.post("/api/book")
@login_required
def book_api():
    if current_user.role != "patient":
        return jsonify(error="Patient access required"), 403
    payload = __import__("flask").request.get_json(silent=True) or {}
    required = {"doctorId", "date", "time", "reason"}
    if not required.issubset(payload):
        return jsonify(error="doctorId, date, time, and reason are required"), 400
    return jsonify(error="Use the web booking form for CSRF-protected booking"), 400
