from datetime import date

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from models import Admin, Appointment, Doctor, Patient, Prescription

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/dashboard")
@login_required
def dashboard():
    if current_user.role == "patient":
        appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).all()
        prescriptions = Prescription.query.join(Appointment).filter(Appointment.patient_id == current_user.id).order_by(Prescription.issued_at.desc()).all()
    elif current_user.role == "doctor":
        appointments = Appointment.query.filter_by(doctor_id=current_user.id, appointment_date=date.today()).order_by(Appointment.appointment_time).all()
        prescriptions = []
    else:
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
        prescriptions = []
    return render_template("dashboard.html", appointments=appointments, prescriptions=prescriptions)


@main_bp.get("/doctors")
def doctors():
    return render_template("doctors.html", doctors=Doctor.query.filter_by(is_active=True).order_by(Doctor.full_name).all())


@main_bp.get("/appointments/history")
@login_required
def appointment_history():
    if current_user.role != "patient":
        return dashboard()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date.desc()).all()
    return render_template("appointments.html", appointments=appointments)


@main_bp.get("/prescriptions")
@login_required
def prescriptions():
    if current_user.role != "patient":
        return dashboard()
    prescriptions = Prescription.query.join(Appointment).filter(Appointment.patient_id == current_user.id).order_by(Prescription.issued_at.desc()).all()
    return render_template("prescription.html", prescriptions=prescriptions)


@main_bp.get("/api/doctors")
def doctors_api():
    doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.full_name).all()
    return jsonify([{"id": doctor.id, "name": doctor.full_name, "specialty": doctor.specialty} for doctor in doctors])


@main_bp.get("/api/appointments")
@login_required
def appointments_api():
    query = Appointment.query.filter_by(patient_id=current_user.id) if current_user.role == "patient" else Appointment.query.filter_by(doctor_id=current_user.id)
    return jsonify([{"appointmentId": item.appointment_id, "date": item.appointment_date.isoformat(), "time": item.appointment_time.isoformat(), "status": item.status, "doctor": item.doctor.full_name, "patient": item.patient.full_name} for item in query.order_by(Appointment.appointment_date.desc()).all()])
