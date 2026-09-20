from flask import Blueprint, request, jsonify
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required,logout_user

from app.services.auth_service import login, change_password


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/csrf-token", methods=["GET"])
def csrf_token():
    return jsonify({
        "success": True,
        "message": "CSRF token generated",
        "data": {
            "csrf_token": generate_csrf()
        },
        "errors": None
    })

@auth_bp.route("/session", methods=["GET"])
@login_required
def session_info():
    return jsonify({
        "success": True,
        "message": "Active session",
        "data": {
            "user_id": current_user.UserID,
            "email": current_user.Email,
            "first_name": current_user.FirstName,
            "last_name": current_user.LastName,
            "role_id": current_user.RoleID
        },
        "errors": None
    }), 200

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout_route():
    logout_user()

    return jsonify({
        "success": True,
        "message": "Logout successful",
        "data": None,
        "errors": None
    }), 200


@auth_bp.route("/login", methods=["POST"])
def login_route():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required",
            "data": None,
            "errors": None
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required",
            "data": None,
            "errors": None
        }), 400

    result = login(email, password)

    return jsonify({
        "success": result["success"],
        "message": result["message"],
        "data": result["data"],
        "errors": None
    }), result["status_code"]
@auth_bp.route("/password", methods=["PATCH"])
@login_required
def change_password_route():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required",
            "data": None,
            "errors": None
        }), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({
            "success": False,
            "message": "Current password and new password are required",
            "data": None,
            "errors": None
        }), 400

    result = change_password(current_password, new_password)

    return jsonify({
        "success": result["success"],
        "message": result["message"],
        "data": result["data"],
        "errors": None
    }), result["status_code"]
