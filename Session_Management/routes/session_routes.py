from flask import Blueprint, request, jsonify, make_response, g
from flask_login import logout_user

from app.config import Config
from Session_Management.services.session_service import SessionService
from Session_Management.middleware.session_middleware import require_session, extract_session_id
from app.repositories.auth_repository import get_user_by_email
from werkzeug.security import check_password_hash


session_bp = Blueprint("session", __name__)


def set_session_cookie(response, session_id: str):
    """Attach the secure HttpOnly session cookie to an HTTP response."""
    max_age_seconds = Config.SESSION_LIFETIME_MINUTES * 60
    cookie_name = getattr(Config, "AUTH_COOKIE_NAME", "session_id")
    response.set_cookie(
        key=cookie_name,
        value=session_id,
        max_age=max_age_seconds,
        httponly=Config.SESSION_COOKIE_HTTPONLY,
        secure=Config.SESSION_COOKIE_SECURE,
        samesite=Config.SESSION_COOKIE_SAMESITE,
        path="/"
    )
    return response


def clear_session_cookie(response):
    """Delete session cookie on logout or invalidation."""
    cookie_name = getattr(Config, "AUTH_COOKIE_NAME", "session_id")
    response.delete_cookie(
        key=cookie_name,
        path="/",
        httponly=Config.SESSION_COOKIE_HTTPONLY,
        secure=Config.SESSION_COOKIE_SECURE,
        samesite=Config.SESSION_COOKIE_SAMESITE
    )
    return response


# ============================================================================
# Core Session API (both /api/session/... and /api/v1/sessions/... paths)
# ============================================================================

@session_bp.route("/api/session/create", methods=["POST"])
def session_create_endpoint():
    """
    Dedicated endpoint to create a secure session.
    Accepts JSON with { email, password } to authenticate and issue a session.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required to create a session",
            "data": None,
            "errors": "VALIDATION_ERROR"
        }), 400

    user = get_user_by_email(email)
    if not user or not check_password_hash(user.PasswordHash, password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password",
            "data": None,
            "errors": "INVALID_CREDENTIALS"
        }), 401

    if not user.IsActive:
        return jsonify({
            "success": False,
            "message": "User account is disabled",
            "data": None,
            "errors": "USER_DISABLED"
        }), 403

    session = SessionService.create_session(user, request)

    role_names = {1: "ADMIN", 2: "FACULTY", 3: "STUDENT"}
    payload = {
        "session_id": session.SessionID,
        "expires_at": session.ExpiresAt.isoformat(),
        "user": {
            "user_id": user.UserID,
            "email": user.Email,
            "first_name": user.FirstName,
            "last_name": user.LastName,
            "role_id": user.RoleID,
            "role_name": role_names.get(user.RoleID, "USER")
        }
    }

    res = make_response(jsonify({
        "success": True,
        "message": "Session created successfully",
        "data": payload,
        "errors": None
    }), 201)

    return set_session_cookie(res, session.SessionID)


@session_bp.route("/api/session/current", methods=["GET"])
@session_bp.route("/api/v1/sessions/current", methods=["GET"])
@require_session
def session_current_endpoint():
    """Retrieve details for the current active session."""
    session = g.current_session
    user = g.current_user

    role_names = {1: "ADMIN", 2: "FACULTY", 3: "STUDENT"}
    payload = {
        "session_id": session.SessionID,
        "created_at": session.CreatedAt.isoformat(),
        "last_activity_at": session.LastActivityAt.isoformat(),
        "expires_at": session.ExpiresAt.isoformat(),
        "ip_address": session.IPAddress,
        "user_agent": session.UserAgent,
        "user": {
            "user_id": user.UserID,
            "email": user.Email,
            "first_name": user.FirstName,
            "last_name": user.LastName,
            "role_id": user.RoleID,
            "role_name": role_names.get(user.RoleID, "USER")
        }
    }

    return jsonify({
        "success": True,
        "message": "Current session details retrieved",
        "data": payload,
        "errors": None
    }), 200


@session_bp.route("/api/session/validate", methods=["GET"])
@session_bp.route("/api/v1/sessions/validate", methods=["GET"])
@require_session
def session_validate_endpoint():
    """Validate that the session is active, valid, and unexpired."""
    session = g.current_session
    user = g.current_user

    role_names = {1: "ADMIN", 2: "FACULTY", 3: "STUDENT"}
    return jsonify({
        "success": True,
        "message": "Session is valid and active",
        "data": {
            "is_valid": True,
            "session_id": session.SessionID,
            "expires_at": session.ExpiresAt.isoformat(),
            "user": {
                "user_id": user.UserID,
                "email": user.Email,
                "role_id": user.RoleID,
                "role_name": role_names.get(user.RoleID, "USER")
            }
        },
        "errors": None
    }), 200


@session_bp.route("/api/session/refresh", methods=["POST"])
@session_bp.route("/api/v1/sessions/refresh", methods=["POST"])
@require_session
def session_refresh_endpoint():
    """Extend the current session lifetime and refresh cookie."""
    session = g.current_session
    success, result = SessionService.refresh_session(session.SessionID, request)

    if not success:
        return jsonify({
            "success": False,
            "message": result.get("message", "Failed to refresh session"),
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


@session_bp.route("/api/session/logout", methods=["POST"])
@require_session
def session_logout_endpoint():
    """Destroy the current session in database and delete cookie."""
    session = g.current_session
    SessionService.destroy_session(session.SessionID)
    try:
        logout_user()
    except Exception:
        pass

    res = make_response(jsonify({
        "success": True,
        "message": "Logged out and session destroyed successfully",
        "data": None,
        "errors": None
    }), 200)

    return clear_session_cookie(res)


# ============================================================================
# Admin Session Management Endpoints
# ============================================================================

@session_bp.route("/api/v1/sessions", methods=["GET"])
@session_bp.route("/api/sessions", methods=["GET"])
@require_session(allowed_roles=[1])  # Admin only
def list_sessions_admin():
    """List all currently active sessions across all users (Admin view)."""
    active_sessions = SessionService.list_active_sessions()

    return jsonify({
        "success": True,
        "message": "Active sessions retrieved successfully",
        "data": {
            "total_active": len(active_sessions),
            "sessions": active_sessions
        },
        "errors": None
    }), 200


@session_bp.route("/api/v1/sessions/<session_id>", methods=["DELETE"])
@session_bp.route("/api/sessions/<session_id>", methods=["DELETE"])
@require_session
def terminate_session_endpoint(session_id):
    """
    Invalidate a specific session.
    Allowed for:
      - Admin users (can invalidate any session)
      - Standard users (can invalidate their own session)
    """
    current_user = g.current_user
    current_session = g.current_session

    is_admin = (current_user.RoleID == 1)
    is_own_session = (current_session.SessionID == session_id)

    if not is_admin and not is_own_session:
        return jsonify({
            "success": False,
            "message": "Forbidden. You can only terminate your own session.",
            "data": None,
            "errors": "FORBIDDEN"
        }), 403

    success = SessionService.force_terminate_session(session_id, admin_user_id=current_user.UserID)

    if not success:
        return jsonify({
            "success": False,
            "message": "Session not found or already invalidated.",
            "data": None,
            "errors": "NOT_FOUND"
        }), 404

    res = make_response(jsonify({
        "success": True,
        "message": "Session invalidated successfully",
        "data": None,
        "errors": None
    }), 200)

    if is_own_session:
        res = clear_session_cookie(res)

    return res
