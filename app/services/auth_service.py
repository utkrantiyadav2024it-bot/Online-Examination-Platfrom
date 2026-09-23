from flask_login import login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories.auth_repository import get_user_by_email, update_password
from app.repositories.audit_repository import create_audit_log


def login(email, password):
    user = get_user_by_email(email)

    # Invalid email or password
    if not user or not check_password_hash(user.PasswordHash, password):
        create_audit_log(
            user_id=user.UserID if user else None,
            action="LOGIN",
            status="FAILED",
            details="Invalid email or password"
        )

        return {
            "success": False,
            "status_code": 401,
            "message": "Invalid email or password",
            "data": None
        }

    # Account is disabled
    if not user.IsActive:
        create_audit_log(
            user_id=user.UserID,
            action="LOGIN",
            status="FAILED",
            details="User account is disabled"
        )

        return {
            "success": False,
            "status_code": 403,
            "message": "User account is disabled",
            "data": None
        }

    # Create Flask-Login session
    login_user(user)

    # Record successful login
    create_audit_log(
        user_id=user.UserID,
        action="LOGIN",
        status="SUCCESS",
        details="User logged in successfully"
    )

    return {
        "success": True,
        "status_code": 200,
        "message": "Login successful",
        "data": {
            "user_id": user.UserID,
            "email": user.Email,
            "first_name": user.FirstName,
            "last_name": user.LastName,
            "role_id": user.RoleID
        }
    }


def change_password(current_password, new_password):
    user = current_user

    # Verify current password
    if not check_password_hash(user.PasswordHash, current_password):
        create_audit_log(
            user_id=user.UserID,
            action="PASSWORD_CHANGE",
            status="FAILED",
            details="Current password is incorrect"
        )

        return {
            "success": False,
            "status_code": 401,
            "message": "Current password is incorrect",
            "data": None
        }

    # Check new password length
    if len(new_password) < 8:
        return {
            "success": False,
            "status_code": 400,
            "message": "New password must be at least 8 characters",
            "data": None
        }

    # Generate new password hash
    new_password_hash = generate_password_hash(new_password)

    # Update database
    update_password(user, new_password_hash)

    # Record successful password change
    create_audit_log(
        user_id=user.UserID,
        action="PASSWORD_CHANGE",
        status="SUCCESS",
        details="Password changed successfully"
    )

    return {
        "success": True,
        "status_code": 200,
        "message": "Password changed successfully",
        "data": None
    }
