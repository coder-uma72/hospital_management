from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from models import db, Patient, Doctor, Appointment
from routes.auth_helpers import get_current_doctor


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


def require_admin():

    verify_jwt_in_request()

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    return None


def get_role():

    verify_jwt_in_request()

    claims = get_jwt()

    return claims.get("role")


@api_bp.route("/patients", methods=["GET"])
def api_get_patients():

    error = require_admin()

    if error:
        return error

    patients = Patient.query.all()

    return jsonify([
        {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
        for patient in patients
    ]), 200


@api_bp.route("/patients", methods=["POST"])
def api_create_patient():

    error = require_admin()

    if error:
        return error

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or not age or not gender or not contact:
        return jsonify({
            "message": "name, age, gender and contact are required"
        }), 400

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Age must be a number"
        }), 400

    existing_patient = Patient.query.filter_by(
        contact=contact
    ).first()

    if existing_patient:
        return jsonify({
            "message": "Contact already exists"
        }), 409

    patient = Patient(
        name=name,
        age=age,
        gender=gender,
        contact=contact
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient created successfully",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 201


@api_bp.route("/patients/<int:id>", methods=["GET"])
def api_get_patient(id):

    error = require_admin()

    if error:
        return error

    patient = Patient.query.get_or_404(id)

    return jsonify({
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "contact": patient.contact
    }), 200


@api_bp.route("/patients/<int:id>", methods=["PUT"])
def api_update_patient(id):

    error = require_admin()

    if error:
        return error

    patient = Patient.query.get_or_404(id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or not age or not gender or not contact:
        return jsonify({
            "message": "name, age, gender and contact are required"
        }), 400

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({
            "message": "Age must be a number"
        }), 400

    existing_patient = Patient.query.filter(
        Patient.contact == contact,
        Patient.id != id
    ).first()

    if existing_patient:
        return jsonify({
            "message": "Contact already exists"
        }), 409

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = contact

    db.session.commit()

    return jsonify({
        "message": "Patient updated successfully"
    }), 200


@api_bp.route("/patients/<int:id>", methods=["PATCH"])
def api_patch_patient(id):

    error = require_admin()

    if error:
        return error

    patient = Patient.query.get_or_404(id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "name" in data:
        patient.name = data["name"]

    if "age" in data:

        try:
            patient.age = int(data["age"])
        except (TypeError, ValueError):
            return jsonify({
                "message": "Age must be a number"
            }), 400

    if "gender" in data:
        patient.gender = data["gender"]

    if "contact" in data:

        existing_patient = Patient.query.filter(
            Patient.contact == data["contact"],
            Patient.id != id
        ).first()

        if existing_patient:
            return jsonify({
                "message": "Contact already exists"
            }), 409

        patient.contact = data["contact"]

    db.session.commit()

    return jsonify({
        "message": "Patient partially updated successfully"
    }), 200


@api_bp.route("/patients/<int:id>", methods=["DELETE"])
def api_delete_patient(id):

    error = require_admin()

    if error:
        return error

    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient deleted successfully"
    }), 200


@api_bp.route("/doctors", methods=["GET"])
def api_get_doctors():

    error = require_admin()

    if error:
        return error

    doctors = Doctor.query.all()

    return jsonify([
        {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
        for doctor in doctors
    ]), 200


@api_bp.route("/doctors", methods=["POST"])
def api_create_doctor():

    error = require_admin()

    if error:
        return error

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return jsonify({
            "message": "name and specialization are required"
        }), 400

    doctor = Doctor(
        name=name,
        specialization=specialization
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor created successfully",
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 201


@api_bp.route("/doctors/<int:id>", methods=["GET"])
def api_get_doctor(id):

    error = require_admin()

    if error:
        return error

    doctor = Doctor.query.get_or_404(id)

    return jsonify({
        "id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization
    }), 200


@api_bp.route("/doctors/<int:id>", methods=["PUT"])
def api_update_doctor(id):

    error = require_admin()

    if error:
        return error

    doctor = Doctor.query.get_or_404(id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return jsonify({
            "message": "name and specialization are required"
        }), 400

    doctor.name = name
    doctor.specialization = specialization

    db.session.commit()

    return jsonify({
        "message": "Doctor updated successfully"
    }), 200


@api_bp.route("/doctors/<int:id>", methods=["PATCH"])
def api_patch_doctor(id):

    error = require_admin()

    if error:
        return error

    doctor = Doctor.query.get_or_404(id)

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "name" in data:
        doctor.name = data["name"]

    if "specialization" in data:
        doctor.specialization = data["specialization"]

    db.session.commit()

    return jsonify({
        "message": "Doctor partially updated successfully"
    }), 200


@api_bp.route("/doctors/<int:id>", methods=["DELETE"])
def api_delete_doctor(id):

    error = require_admin()

    if error:
        return error

    doctor = Doctor.query.get_or_404(id)

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor deleted successfully"
    }), 200


@api_bp.route("/appointments", methods=["GET"])
def api_get_appointments():

    role = get_role()

    doctor_id = request.args.get("doctor_id")

    if role == "admin":

        if doctor_id:

            try:
                doctor_id = int(doctor_id)
            except ValueError:
                return jsonify({
                    "message": "doctor_id must be a number"
                }), 400

            appointments = Appointment.query.filter_by(
                doctor_id=doctor_id
            ).all()

        else:

            appointments = Appointment.query.all()

    elif role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return jsonify({
                "message": "Doctor record not found"
            }), 404

        appointments = Appointment.query.filter_by(
            doctor_id=doctor.id
        ).all()

    else:

        return jsonify({
            "message": "Access denied"
        }), 403

    return jsonify([
        {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "date": appointment.date.isoformat(),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        }
        for appointment in appointments
    ]), 200


@api_bp.route("/appointments", methods=["POST"])
def api_create_appointment():

    error = require_admin()

    if error:
        return error

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("date")
    diagnosis = data.get("diagnosis")
    status = data.get("status")

    if not patient_id or not doctor_id or not appointment_date or not diagnosis or not status:
        return jsonify({
            "message": "patient_id, doctor_id, date, diagnosis and status are required"
        }), 400

    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "message": "Invalid status",
            "allowed_statuses": allowed_statuses
        }), 400

    try:

        appointment_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

    except (TypeError, ValueError):

        return jsonify({
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=appointment_date,
        diagnosis=diagnosis,
        status=status
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment created successfully",
        "appointment": {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.date.isoformat(),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        }
    }), 201


@api_bp.route("/appointments/<int:id>", methods=["GET"])
def api_get_appointment(id):

    role = get_role()

    appointment = Appointment.query.get_or_404(id)

    if role == "doctor":

        doctor = get_current_doctor()

        if not doctor:
            return jsonify({
                "message": "Doctor record not found"
            }), 404

        if appointment.doctor_id != doctor.id:
            return jsonify({
                "message": "You can only view your own appointments"
            }), 403

    elif role != "admin":

        return jsonify({
            "message": "Access denied"
        }), 403

    return jsonify({
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": appointment.patient.name,
        "doctor_id": appointment.doctor_id,
        "doctor_name": appointment.doctor.name,
        "date": appointment.date.isoformat(),
        "diagnosis": appointment.diagnosis,
        "status": appointment.status
    }), 200


@api_bp.route("/appointments/<int:id>", methods=["PUT"])
def api_update_appointment(id):

    role = get_role()

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

    elif role != "admin":

        return jsonify({
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("date")
    diagnosis = data.get("diagnosis")
    status = data.get("status")

    if not patient_id or not doctor_id or not appointment_date or not diagnosis or not status:
        return jsonify({
            "message": "patient_id, doctor_id, date, diagnosis and status are required"
        }), 400

    patient = Patient.query.get(patient_id)
    doctor = Doctor.query.get(doctor_id)

    if not patient:
        return jsonify({
            "message": "Patient not found"
        }), 404

    if not doctor:
        return jsonify({
            "message": "Doctor not found"
        }), 404

    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "message": "Invalid status"
        }), 400

    try:

        appointment_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

    except (TypeError, ValueError):

        return jsonify({
            "message": "Date must be in YYYY-MM-DD format"
        }), 400

    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.date = appointment_date
    appointment.diagnosis = diagnosis
    appointment.status = status

    db.session.commit()

    return jsonify({
        "message": "Appointment updated successfully"
    }), 200


@api_bp.route("/appointments/<int:id>", methods=["PATCH"])
def api_patch_appointment(id):

    role = get_role()

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

    elif role != "admin":

        return jsonify({
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    if "patient_id" in data:

        patient = Patient.query.get(data["patient_id"])

        if not patient:
            return jsonify({
                "message": "Patient not found"
            }), 404

        appointment.patient_id = data["patient_id"]

    if "doctor_id" in data:

        doctor = Doctor.query.get(data["doctor_id"])

        if not doctor:
            return jsonify({
                "message": "Doctor not found"
            }), 404

        appointment.doctor_id = data["doctor_id"]

    if "date" in data:

        try:

            appointment.date = datetime.strptime(
                data["date"],
                "%Y-%m-%d"
            ).date()

        except (TypeError, ValueError):

            return jsonify({
                "message": "Date must be in YYYY-MM-DD format"
            }), 400

    if "diagnosis" in data:
        appointment.diagnosis = data["diagnosis"]

    if "status" in data:

        allowed_statuses = [
            "Recovered",
            "Under Treatment",
            "Critical"
        ]

        if data["status"] not in allowed_statuses:
            return jsonify({
                "message": "Invalid status"
            }), 400

        appointment.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Appointment partially updated successfully"
    }), 200


@api_bp.route("/appointments/<int:id>", methods=["DELETE"])
def api_delete_appointment(id):

    error = require_admin()

    if error:
        return error

    appointment = Appointment.query.get_or_404(id)

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment cancelled successfully"
    }), 200