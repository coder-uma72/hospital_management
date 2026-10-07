from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for
)

from models import db, Doctor
from routes.auth_helpers import admin_required


doctors_bp = Blueprint(
    "doctors",
    __name__,
    url_prefix="/doctors"
)


@doctors_bp.route("/", methods=["GET"], strict_slashes=False)
@admin_required
def get_doctors():

    doctors = Doctor.query.all()

    return render_template(
        "doctors/list.html",
        doctors=doctors
    )


@doctors_bp.route("/new", methods=["GET"])
@admin_required
def new_doctor():

    return render_template(
        "doctors/new.html"
    )


@doctors_bp.route("/", methods=["POST"], strict_slashes=False)
@admin_required
def create_doctor():

    name = request.form.get("name")
    specialization = request.form.get("specialization")

    if not name or not specialization:
        return "All fields are required", 400

    doctor = Doctor(
        name=name,
        specialization=specialization
    )

    db.session.add(doctor)
    db.session.commit()

    return redirect(
        url_for("doctors.get_doctors")
    )


@doctors_bp.route("/<int:id>", methods=["GET"])
@admin_required
def get_doctor(id):

    doctor = Doctor.query.get_or_404(id)

    return render_template(
        "doctors/details.html",
        doctor=doctor
    )


@doctors_bp.route("/<int:id>/edit", methods=["GET"])
@admin_required
def edit_doctor(id):

    doctor = Doctor.query.get_or_404(id)

    return render_template(
        "doctors/edit.html",
        doctor=doctor
    )


@doctors_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_doctor(id):

    doctor = Doctor.query.get_or_404(id)

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return "All fields are required", 400

    doctor.name = name
    doctor.specialization = specialization

    db.session.commit()

    if request.is_json:
        return jsonify({
            "message": "Doctor updated successfully"
        })

    return redirect(
        url_for(
            "doctors.get_doctor",
            id=id
        )
    )


@doctors_bp.route("/<int:id>", methods=["PATCH"])
@admin_required
def patch_doctor(id):

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
    })


@doctors_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_doctor(id):

    doctor = Doctor.query.get_or_404(id)

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({
        "message": "Doctor deleted successfully"
    })