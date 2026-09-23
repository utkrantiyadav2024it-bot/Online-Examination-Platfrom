"""
Audit Logging - HTTP layer.

Base path: /api/v1/audit
Access:    ADMIN only (the audit trail is a governance surface).
"""

from flask import Blueprint, Response, request

from app.services import audit_service
from app.utils.api_response import error_response, success_response
from app.utils.rbac import roles_required

audit_bp = Blueprint("audit", __name__, url_prefix="/api/v1/audit")


def _envelope(result):
    if result["success"]:
        return success_response(
            data=result.get("data"),
            message=result.get("message", "OK"),
            status_code=result.get("status_code", 200)
        )

    return error_response(
        message=result.get("message", "Request failed"),
        status_code=result.get("status_code", 400),
        errors=result.get("errors")
    )


@audit_bp.route("/logs", methods=["GET"])
@roles_required("ADMIN")
def list_logs_route():
    """
    Paginated, filterable audit trail.

    Query params: search, module, action, status, entity_name, user_id,
                  exam_attempt_id, start_date, end_date, page, page_size
    """
    return _envelope(audit_service.list_logs(request.args))


@audit_bp.route("/logs/<int:audit_log_id>", methods=["GET"])
@roles_required("ADMIN")
def get_log_route(audit_log_id):
    return _envelope(audit_service.get_log(audit_log_id))


@audit_bp.route("/filters", methods=["GET"])
@roles_required("ADMIN")
def filter_options_route():
    """Distinct modules / actions / statuses present in the ledger."""
    return _envelope(audit_service.get_filter_options())


@audit_bp.route("/summary", methods=["GET"])
@roles_required("ADMIN")
def summary_route():
    return _envelope(audit_service.get_summary())


@audit_bp.route("/logs/export", methods=["GET"])
@roles_required("ADMIN")
def export_logs_route():
    """CSV download honouring the same filters as /logs."""
    csv_text, filename = audit_service.export_logs_csv(request.args)

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="{}"'.format(filename)
        }
    )


@audit_bp.route("/logs", methods=["POST"])
@roles_required("ADMIN", "FACULTY", "STUDENT")
def create_log_route():
    """
    Append an entry to the ledger.

    Used for client-observed events (e.g. exam-integrity signals). Requires a
    CSRF token from GET /api/v1/auth/csrf-token in the X-CSRFToken header.
    """
    payload = request.get_json(silent=True)
    return _envelope(audit_service.create_log_from_request(payload))
