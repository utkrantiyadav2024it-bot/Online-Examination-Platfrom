"""
Role based access control helpers.

The Role table is seeded by schema.sql with ADMIN / FACULTY / STUDENT.
Role names are resolved from the database (not hard-coded IDs) and cached for
the lifetime of the process, so renaming or re-seeding roles keeps working.
"""

from functools import wraps

from flask_login import current_user, login_required

from app.extensions import db
from app.utils.api_response import error_response

_ROLE_NAME_CACHE = {}


def get_role_name(role_id):
    """Return the upper-cased role name for a RoleID, or None."""
    if role_id is None:
        return None

    role_id = int(role_id)
    if role_id in _ROLE_NAME_CACHE:
        return _ROLE_NAME_CACHE[role_id]

    row = db.session.execute(
        db.text("SELECT RoleName FROM Role WHERE RoleID = :role_id"),
        {"role_id": role_id}
    ).first()

    if not row:
        return None

    _ROLE_NAME_CACHE[role_id] = str(row[0]).strip().upper()
    return _ROLE_NAME_CACHE[role_id]


def current_role():
    if not current_user.is_authenticated:
        return None
    return get_role_name(current_user.RoleID)


def roles_required(*allowed_roles):
    """
    Restrict a view to the given roles.

    401 if not logged in (handled by flask_login), 403 if logged in with a
    role that is not permitted.
    """
    allowed = {role.strip().upper() for role in allowed_roles}

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(*args, **kwargs):
            role_name = get_role_name(current_user.RoleID)

            if role_name not in allowed:
                return error_response(
                    message="You do not have permission to access this resource",
                    status_code=403,
                    errors={"required_roles": sorted(allowed)}
                )

            return view_func(*args, **kwargs)

        return wrapper

    return decorator
