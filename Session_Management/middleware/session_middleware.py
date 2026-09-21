from functools import wraps
from typing import List, Optional, Union
from flask import request, jsonify, g
from flask_login import login_user, current_user

from app.config import Config
from Session_Management.services.session_service import SessionService


def extract_session_id() -> Optional[str]:
    """
    Extract session token in order of precedence:
    1. Authorization Header (`Bearer <token>`)
    2. Custom Header (`X-Session-ID`)
    3. HttpOnly Cookie (`session_id` or configured AUTH_COOKIE_NAME)
    """
    # 1. Authorization Bearer
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        parts = auth_header.split(" ", 1)
        if len(parts) == 2 and parts[1].strip():
            return parts[1].strip()

    # 2. Custom Header
    header_token = request.headers.get("X-Session-ID")
    if header_token:
        return header_token.strip()

    # 3. Cookie
    cookie_name = getattr(Config, "AUTH_COOKIE_NAME", "session_id")
    token = request.cookies.get(cookie_name)
    if not token and cookie_name != "session_id":
        token = request.cookies.get("session_id")
    if token:
        return token

    return None


def require_session(allowed_roles: Optional[Union[List[Union[int, str]], int, str]] = None):
    """
    Session protection decorator.
    Can be used as:
        @require_session
        or
        @require_session(allowed_roles=[1, 2])
        or
        @require_session(allowed_roles=["ADMIN", "FACULTY"])
    """
    # Handle usage without parentheses: @require_session
    if callable(allowed_roles):
        fn = allowed_roles
        allowed_roles = None

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return _execute_session_check(fn, None, *args, **kwargs)

        return wrapper

    # Normalize allowed_roles to a list
    if allowed_roles is not None and not isinstance(allowed_roles, (list, tuple, set)):
        roles_list = [allowed_roles]
    else:
        roles_list = list(allowed_roles) if allowed_roles is not None else None

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return _execute_session_check(fn, roles_list, *args, **kwargs)

        return wrapper

    return decorator


def _execute_session_check(fn, roles_list, *args, **kwargs):
    session_id = extract_session_id()

    if not session_id:
        return jsonify({
            "success": False,
            "message": "Authentication required. Missing session token.",
            "data": None,
            "errors": "MISSING_SESSION"
        }), 401

    is_valid, validation_result = SessionService.validate_session(session_id, request)

    if not is_valid:
        error_code = validation_result.get("error", "INVALID_SESSION")
        message = validation_result.get("message", "Invalid or expired session.")
        return jsonify({
            "success": False,
            "message": message,
            "data": None,
            "errors": error_code
        }), 401

    session = validation_result["session"]
    user = validation_result["user"]

    if not user or not user.IsActive:
        return jsonify({
            "success": False,
            "message": "User account is disabled or not found.",
            "data": None,
            "errors": "USER_DISABLED"
        }), 403

    # Bind to Flask `g`
    g.current_session = session
    g.current_user = user

    # Sync with Flask-Login for backward compatibility with existing routes
    try:
        if not current_user.is_authenticated:
            login_user(user, remember=False)
    except Exception:
        pass

    # RBAC Role Checking if specified
    if roles_list:
        user_role_id = user.RoleID
        role_matches = False

        role_name_map = {1: "ADMIN", 2: "FACULTY", 3: "STUDENT"}

        for req_role in roles_list:
            if isinstance(req_role, int) and user_role_id == req_role:
                role_matches = True
                break
            elif isinstance(req_role, str):
                if req_role.upper() == role_name_map.get(user_role_id, "").upper():
                    role_matches = True
                    break

        if not role_matches:
            return jsonify({
                "success": False,
                "message": "Forbidden. Insufficient permissions for this resource.",
                "data": None,
                "errors": "FORBIDDEN"
            }), 403

    return fn(*args, **kwargs)
