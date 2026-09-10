from datetime import datetime, timezone
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager


class AppointmentStatus(str, Enum):
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


class Patient(UserMixin, db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    @property
    def role(self):
        return "patient"

    def get_id(self):
        return f"patient:{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Doctor(UserMixin, db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    appointments = db.relationship("Appointment", back_populates="doctor")

    @property
    def role(self):
        return "doctor"

    def get_id(self):
        return f"doctor:{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    @property
    def role(self):
        return "admin"

    def get_id(self):
        return f"admin:{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    queue_token = db.Column(db.Integer, nullable=False)
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    fee = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=AppointmentStatus.CONFIRMED.value, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    prescription = db.relationship("Prescription", back_populates="appointment", uselist=False, cascade="all, delete-orphan")


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    medicines = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    issued_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    appointment = db.relationship("Appointment", back_populates="prescription")
    doctor = db.relationship("Doctor")


@login_manager.user_loader
def load_user(user_id):
    role, _, raw_id = user_id.partition(":")
    model = {"patient": Patient, "doctor": Doctor, "admin": Admin}.get(role)
    return model.query.get(int(raw_id)) if model and raw_id.isdigit() else None


def user_identity(user):
    return f"{user.role}:{user.id}"
