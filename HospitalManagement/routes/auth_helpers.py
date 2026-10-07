from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from models import User, Doctor


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        claims = get_jwt()

        if claims.get("role") != "admin":
            return jsonify({
                "message": "Admin access required"
            }), 403

        return function(*args, **kwargs)

    return wrapper


def doctor_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        claims = get_jwt()

        if claims.get("role") != "doctor":
            return jsonify({
                "message": "Doctor access required"
            }), 403

        return function(*args, **kwargs)

    return wrapper


def get_current_user():

    user_id = get_jwt_identity()

    return User.query.get(int(user_id))


def get_current_doctor():

    user = get_current_user()

    if not user or user.role != "doctor":
        return None

    doctor = Doctor.query.filter_by(
        name=user.name
    ).first()

    return doctor