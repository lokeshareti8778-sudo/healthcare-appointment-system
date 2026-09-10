from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=30)])
    date_of_birth = DateField("Date of birth", validators=[Optional()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    role = SelectField("Account type", choices=[("patient", "Patient"), ("doctor", "Doctor"), ("admin", "Administrator")])
    remember = SelectField("Keep me signed in", choices=[("no", "No"), ("yes", "Yes")], default="no")
    submit = SubmitField("Sign in")


class AppointmentForm(FlaskForm):
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    appointment_date = DateField("Date", validators=[DataRequired()])
    appointment_time = TimeField("Time", validators=[DataRequired()])
    reason = TextAreaField("Reason for visit", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Confirm appointment")


class StatusForm(FlaskForm):
    status = SelectField("Status", choices=[("Confirmed", "Confirmed"), ("Completed", "Completed"), ("Cancelled", "Cancelled"), ("No Show", "No Show")], validators=[DataRequired()])
    submit = SubmitField("Update status")


class PrescriptionForm(FlaskForm):
    medicines = TextAreaField("Medicines", validators=[DataRequired(), Length(max=4000)])
    instructions = TextAreaField("Instructions", validators=[DataRequired(), Length(max=4000)])
    submit = SubmitField("Save prescription")


class DoctorForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    specialty = StringField("Specialty", validators=[DataRequired(), Length(max=120)])
    license_number = StringField("License number", validators=[DataRequired(), Length(max=80)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    bio = TextAreaField("Biography", validators=[Optional(), Length(max=4000)])
    password = PasswordField("Initial password", validators=[Optional(), Length(min=8)])
    submit = SubmitField("Save doctor")
