from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)

from flask_jwt_extended import jwt_required

from models import db, Patient
from routes.auth_helpers import admin_required


patients_bp = Blueprint(
    "patients",
    __name__,
    url_prefix="/patients"
)


@patients_bp.route("/", methods=["GET"], strict_slashes=False)
@admin_required
def get_patients():

    patients = Patient.query.all()

    return render_template(
        "patients/list.html",
        patients=patients
    )


@patients_bp.route("/new", methods=["GET"])
@admin_required
def new_patient():

    return render_template(
        "patients/new.html"
    )


@patients_bp.route("/", methods=["POST"], strict_slashes=False)
@admin_required
def create_patient():

    name = request.form.get("name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    contact = request.form.get("contact")

    if not name or not age or not gender or not contact:
        return "All fields are required", 400

    try:
        age = int(age)
    except ValueError:
        return "Age must be a number", 400

    existing_patient = Patient.query.filter_by(
        contact=contact
    ).first()

    if existing_patient:
        return "Contact already exists", 409

    patient = Patient(
        name=name,
        age=age,
        gender=gender,
        contact=contact
    )

    db.session.add(patient)
    db.session.commit()

    return redirect(
        url_for("patients.get_patients")
    )


@patients_bp.route("/<int:id>", methods=["GET"])
@admin_required
def get_patient(id):

    patient = Patient.query.get_or_404(id)

    return render_template(
        "patients/details.html",
        patient=patient
    )


@patients_bp.route("/<int:id>/edit", methods=["GET"])
@admin_required
def edit_patient(id):

    patient = Patient.query.get_or_404(id)

    return render_template(
        "patients/edit.html",
        patient=patient
    )


@patients_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_patient(id):

    patient = Patient.query.get_or_404(id)

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or not age or not gender or not contact:
        return "All fields are required", 400

    try:
        age = int(age)
    except ValueError:
        return "Age must be a number", 400

    existing_patient = Patient.query.filter(
        Patient.contact == contact,
        Patient.id != id
    ).first()

    if existing_patient:
        return "Contact already exists", 409

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = contact

    db.session.commit()

    if request.is_json:
        return jsonify({
            "message": "Patient updated successfully"
        })

    return redirect(
        url_for(
            "patients.get_patient",
            id=id
        )
    )


@patients_bp.route("/<int:id>", methods=["PATCH"])
@admin_required
def patch_patient(id):

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
        except ValueError:
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
    })


@patients_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_patient(id):

    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)
    db.session.commit()

    return jsonify({
        "message": "Patient deleted successfully"
    })