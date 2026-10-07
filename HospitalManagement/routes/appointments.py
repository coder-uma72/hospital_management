from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)

from models import db, Appointment, Patient, Doctor
from routes.auth_helpers import admin_required, doctor_required, get_current_doctor


appointments_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/appointments"
)

@appointments_bp.route("/", methods=["GET"], strict_slashes=False)
def get_appointments():

    from flask_jwt_extended import verify_jwt_in_request, get_jwt

    verify_jwt_in_request()

    claims = get_jwt()
    role = claims.get("role")

    if role == "admin":

        appointments = Appointment.query.all()

    elif role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return "Doctor record not found", 404

        appointments = Appointment.query.filter_by(
            doctor_id=doctor.id
        ).all()

    else:

        return "Access denied", 403

    return render_template(
        "appointments/list.html",
        appointments=appointments
    )


@appointments_bp.route("/new", methods=["GET"])
@admin_required
def new_appointment():

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "appointments/new.html",
        patients=patients,
        doctors=doctors
    )

@appointments_bp.route("/", methods=["POST"], strict_slashes=False)
@admin_required
def create_appointment():

    patient_id = request.form.get("patient_id")
    doctor_id = request.form.get("doctor_id")
    appointment_date = request.form.get("date")
    diagnosis = request.form.get("diagnosis")
    status = request.form.get("status")

    if not patient_id or not doctor_id or not appointment_date or not diagnosis or not status:
        return "All fields are required", 400

    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)

    if not patient:
        return "Patient not found", 404

    if not doctor:
        return "Doctor not found", 404

    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:
        return "Invalid appointment status", 400

    try:

        appointment_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return "Invalid date format. Use YYYY-MM-DD", 400

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )

    db.session.add(appointment)
    db.session.commit()

    return redirect(
        url_for("appointments.get_appointments")
    )

@appointments_bp.route("/<int:id>", methods=["GET"])
def get_appointment(id):

    from flask_jwt_extended import verify_jwt_in_request, get_jwt

    verify_jwt_in_request()

    claims = get_jwt()
    role = claims.get("role")

    appointment = Appointment.query.get_or_404(id)

    if role == "admin":

        pass

    elif role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return "Doctor record not found", 404

        if appointment.doctor_id != doctor.id:
            return "Access denied", 403

    else:

        return "Access denied", 403

    return render_template(
        "appointments/details.html",
        appointment=appointment
    )

@appointments_bp.route("/<int:id>/edit", methods=["GET"])
def edit_appointment(id):

    from flask_jwt_extended import verify_jwt_in_request, get_jwt

    verify_jwt_in_request()

    claims = get_jwt()
    role = claims.get("role")

    appointment = Appointment.query.get_or_404(id)

    if role == "admin":

        pass

    elif role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return "Doctor record not found", 404

        if appointment.doctor_id != doctor.id:
            return "Access denied", 403

    else:

        return "Access denied", 403

    patients = Patient.query.all()
    doctors = Doctor.query.all()

    return render_template(
        "appointments/edit.html",
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )


@appointments_bp.route("/<int:id>", methods=["PUT"])
def update_appointment(id):

    from flask_jwt_extended import verify_jwt_in_request, get_jwt

    verify_jwt_in_request()

    claims = get_jwt()
    role = claims.get("role")

    appointment = Appointment.query.get_or_404(id)

    if role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return jsonify({
                "message": "Doctor record not found"
            }), 404

        if appointment.doctor_id != doctor.id:
            return jsonify({
                "message": "You can only update your own appointments"
            }), 403
    
        doctor_id = doctor.id

    elif role != "admin":

        return jsonify({
            "message": "Access denied"
        }), 403

    if request.is_json:

        data = request.get_json()

    else:

        data = request.form

    patient_id = data.get("patient_id")
    if role == "doctor":
        doctor_id = doctor.id
    else:
        doctor_id = data.get("doctor_id")
    appointment_date = data.get("date")
    diagnosis = data.get("diagnosis")
    status = data.get("status")

    if not patient_id or not doctor_id or not appointment_date or not diagnosis or not status:
        return "All fields are required", 400

    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)

    if not patient:
        return "Patient not found", 404

    if not doctor:
        return "Doctor not found", 404

    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:
        return "Invalid appointment status", 400

    try:

        appointment_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return "Invalid date format. Use YYYY-MM-DD", 400

    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.date = appointment_date
    appointment.diagnosis = diagnosis
    appointment.status = status

    db.session.commit()

    if request.is_json:

        return jsonify({
            "message": "Appointment updated successfully"
        })

    return redirect(
        url_for(
            "appointments.get_appointment",
            id=id
        )
    )

@appointments_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_appointment(id):

    appointment = Appointment.query.get_or_404(id)

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment cancelled successfully"
    })