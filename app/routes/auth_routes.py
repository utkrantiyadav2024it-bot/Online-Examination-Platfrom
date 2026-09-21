from flask import Blueprint, request, jsonify, make_response, g
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required, logout_user

from app.services.auth_service import login, change_password
from Session_Management.middleware.session_middleware import require_session, extract_session_id
from Session_Management.services.session_service import SessionService
from Session_Management.routes.session_routes import set_session_cookie, clear_session_cookie


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
@require_session
def session_info():
    """Retrieve active session and identity details."""
    user = g.current_user
    session = g.current_session
    role_names = {1: "ADMIN", 2: "FACULTY", 3: "STUDENT"}

    return jsonify({
        "success": True,
        "message": "Active session",
        "data": {
            "user_id": user.UserID,
            "email": user.Email,
            "first_name": user.FirstName,
            "last_name": user.LastName,
            "role_id": user.RoleID,
            "role_name": role_names.get(user.RoleID, "USER"),
            "session_id": session.SessionID,
            "expires_at": session.ExpiresAt.isoformat(),
            "is_valid": session.is_valid()
        },
        "errors": None
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@require_session
def refresh_session_route():
    """Refresh active session lifetime and refresh cookie."""
    session = g.current_session
    success, result = SessionService.refresh_session(session.SessionID, request)

    if not success:
        return jsonify({
            "success": False,
            "message": result.get("message", "Session refresh failed"),
            "data": None,
            "errors": result.get("error")
        }), 400

    res = make_response(jsonify({
        "success": True,
        "message": "Session refreshed successfully",
        "data": result,
        "errors": None
    }), 200)

    return set_session_cookie(res, session.SessionID)


@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    """Secure logout: invalidates session in DB, logs out user, and deletes cookie."""
    session_id = extract_session_id()
    if session_id:
        SessionService.destroy_session(session_id)

    try:
        logout_user()
    except Exception:
        pass

    res = make_response(jsonify({
        "success": True,
        "message": "Logout successful",
        "data": None,
        "errors": None
    }), 200)

    return clear_session_cookie(res)


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

    res = make_response(jsonify({
        "success": result["success"],
        "message": result["message"],
        "data": result["data"],
        "errors": None
    }), result["status_code"])

    # If login succeeded, attach secure HttpOnly session cookie
    if result["success"] and "session_id" in result.get("data", {}):
        set_session_cookie(res, result["data"]["session_id"])

    return res


@auth_bp.route("/password", methods=["PATCH"])
@require_session
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
