from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)

from models import db, User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/login", methods=["GET"])
def login_page():

    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login():

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        if request.is_json:
            return jsonify({
                "message": "Email and password are required"
            }), 400

        return "Email and password are required", 400

    user = User.query.filter_by(email=email).first()

    if not user:
        if request.is_json:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        return "Invalid email or password", 401

    if not user.check_password(password):
        if request.is_json:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        return "Invalid email or password", 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    if request.is_json:

        response = jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        })

        set_access_cookies(response, access_token)

        return response, 200

    response = redirect(
        url_for("patients.get_patients")
    )

    set_access_cookies(response, access_token)

    return response


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({
            "message": "name, email, password and role are required"
        }), 400

    if role not in ["admin", "doctor"]:
        return jsonify({
            "message": "Role must be admin or doctor"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    user = User(
        name=name,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 201


@auth_bp.route("/logout", methods=["POST"])
def logout():

    response = jsonify({
        "message": "Logged out successfully"
    })

    unset_jwt_cookies(response)

    return response