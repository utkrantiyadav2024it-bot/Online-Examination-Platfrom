"""
Audit Logging - business logic layer.

Responsibilities:
  * validate and normalise incoming filter/pagination parameters
  * shape rows into the JSON the frontend consumes
  * build the CSV export
  * expose record_event(), the reusable writer other modules can call
"""

import csv
import io
from datetime import datetime

from flask import request
from flask_login import current_user

from app.repositories import audit_log_repository as repo
from app.utils.api_response import iso, to_int

MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 25

# Accepted inputs for the date filters (HTML date input sends YYYY-MM-DD).
_DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


def _parse_datetime(value, end_of_day=False):
    if not value:
        return None

    value = str(value).strip()

    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(value, fmt)
            if end_of_day and fmt == "%Y-%m-%d":
                parsed = parsed.replace(hour=23, minute=59, second=59)
            return parsed
        except ValueError:
            continue

    return None


def build_filters(args):
    """Normalise query-string arguments into a filter dict."""
    return {
        "search": (args.get("search") or "").strip() or None,
        "module": (args.get("module") or "").strip() or None,
        "action": (args.get("action") or "").strip() or None,
        "status": (args.get("status") or "").strip() or None,
        "entity_name": (args.get("entity_name") or "").strip() or None,
        "user_id": to_int(args.get("user_id"), None) if args.get("user_id") else None,
        "exam_attempt_id": (
            to_int(args.get("exam_attempt_id"), None)
            if args.get("exam_attempt_id") else None
        ),
        "start_date": _parse_datetime(args.get("start_date")),
        "end_date": _parse_datetime(args.get("end_date"), end_of_day=True),
    }


def build_pagination(args):
    page = to_int(args.get("page"), 1) or 1
    page_size = to_int(args.get("page_size"), DEFAULT_PAGE_SIZE) or DEFAULT_PAGE_SIZE

    page = max(page, 1)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    return page, page_size


def serialise_log(row):
    first_name = row.get("first_name")
    last_name = row.get("last_name")

    if first_name or last_name:
        actor_name = " ".join(part for part in [first_name, last_name] if part)
    else:
        actor_name = "System / Anonymous"

    return {
        "audit_log_id": row.get("audit_log_id"),
        "user_id": row.get("user_id"),
        "actor_name": actor_name,
        "actor_email": row.get("email"),
        "actor_role": row.get("role_name"),
        "exam_attempt_id": row.get("exam_attempt_id"),
        "module": row.get("module"),
        "action": row.get("action"),
        "entity_name": row.get("entity_name"),
        "record_id": row.get("record_id"),
        "target": _format_target(row.get("entity_name"), row.get("record_id")),
        "status": row.get("status"),
        "ip_address": row.get("ip_address"),
        "details": row.get("details"),
        "created_at": iso(row.get("created_at")),
    }


def _format_target(entity_name, record_id):
    if entity_name and record_id:
        return "{} #{}".format(entity_name, record_id)
    if entity_name:
        return entity_name
    if record_id:
        return "#{}".format(record_id)
    return "—"


def list_logs(args):
    filters = build_filters(args)
    page, page_size = build_pagination(args)
    offset = (page - 1) * page_size

    total = repo.count_logs(filters)
    rows = repo.fetch_logs(filters, limit=page_size, offset=offset)

    total_pages = (total + page_size - 1) // page_size if total else 0

    return {
        "success": True,
        "status_code": 200,
        "message": "Audit logs retrieved",
        "data": {
            "items": [serialise_log(row) for row in rows],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next": page < total_pages,
            }
        }
    }


def get_log(audit_log_id):
    row = repo.fetch_log_by_id(audit_log_id)

    if not row:
        return {
            "success": False,
            "status_code": 404,
            "message": "Audit log not found",
            "data": None
        }

    return {
        "success": True,
        "status_code": 200,
        "message": "Audit log retrieved",
        "data": serialise_log(row)
    }


def get_filter_options():
    values = repo.fetch_distinct_values()

    return {
        "success": True,
        "status_code": 200,
        "message": "Audit filter options retrieved",
        "data": values
    }


def get_summary():
    summary = repo.fetch_summary()
    totals = summary["totals"] or {}

    return {
        "success": True,
        "status_code": 200,
        "message": "Audit summary retrieved",
        "data": {
            "total_logs": to_int(totals.get("total_logs")),
            "success_count": to_int(totals.get("success_count")),
            "non_success_count": to_int(totals.get("non_success_count")),
            "last_24h_count": to_int(totals.get("last_24h_count")),
            "distinct_actors": to_int(totals.get("distinct_actors")),
            "first_log_at": iso(totals.get("first_log_at")),
            "last_log_at": iso(totals.get("last_log_at")),
            "by_module": [
                {"module": r.get("module"), "total": to_int(r.get("total"))}
                for r in summary["by_module"]
            ],
            "by_action": [
                {"action": r.get("action"), "total": to_int(r.get("total"))}
                for r in summary["by_action"]
            ],
        }
    }


def export_logs_csv(args):
    """Return (csv_text, filename) for the current filter selection."""
    filters = build_filters(args)
    rows = repo.fetch_all_logs_for_export(filters)

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "AuditLogID", "CreatedAt", "UserID", "Actor", "ActorEmail", "ActorRole",
        "Module", "Action", "EntityName", "RecordID", "ExamAttemptID",
        "Status", "IPAddress", "Details"
    ])

    for row in rows:
        log = serialise_log(row)
        writer.writerow([
            log["audit_log_id"],
            log["created_at"],
            log["user_id"],
            log["actor_name"],
            log["actor_email"],
            log["actor_role"],
            log["module"],
            log["action"],
            log["entity_name"],
            log["record_id"],
            log["exam_attempt_id"],
            log["status"],
            log["ip_address"],
            log["details"],
        ])

    filename = "audit_logs_{}.csv".format(
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    return buffer.getvalue(), filename


def record_event(
    module,
    action,
    status,
    user_id=None,
    entity_name=None,
    record_id=None,
    exam_attempt_id=None,
    details=None,
    ip_address=None
):
    """
    Append one entry to the audit ledger.

    This is the function other modules should import when they need to record
    an event, e.g.:

        from app.services.audit_service import record_event
        record_event("Evaluation", "PUBLISH", "SUCCESS",
                     entity_name="Exam", record_id=exam_id)

    Actor and IP default to the current session / request when not supplied.
    Never raises: a failed audit write must not break the calling operation.
    """
    if not module or not action or not status:
        return None

    if user_id is None:
        try:
            if current_user and current_user.is_authenticated:
                user_id = current_user.UserID
        except Exception:
            user_id = None

    if ip_address is None:
        try:
            ip_address = request.remote_addr
        except Exception:
            ip_address = None

    try:
        return repo.insert_log(
            user_id=user_id,
            module=str(module)[:50],
            action=str(action)[:50],
            status=str(status)[:20],
            entity_name=str(entity_name)[:50] if entity_name else None,
            record_id=record_id,
            exam_attempt_id=exam_attempt_id,
            ip_address=str(ip_address)[:45] if ip_address else None,
            details=details
        )
    except Exception:
        try:
            from app.extensions import db
            db.session.rollback()
        except Exception:
            pass
        return None


def create_log_from_request(payload):
    """Validate and persist an audit entry submitted over the API."""
    if not payload:
        return {
            "success": False,
            "status_code": 400,
            "message": "Request body is required",
            "data": None
        }

    module = (payload.get("module") or "").strip()
    action = (payload.get("action") or "").strip()
    status = (payload.get("status") or "").strip().upper()

    missing = [
        name for name, value in
        (("module", module), ("action", action), ("status", status))
        if not value
    ]

    if missing:
        return {
            "success": False,
            "status_code": 400,
            "message": "module, action and status are required",
            "data": None,
            "errors": {"missing_fields": missing}
        }

    new_id = record_event(
        module=module,
        action=action,
        status=status,
        entity_name=payload.get("entity_name"),
        record_id=to_int(payload.get("record_id"), None)
        if payload.get("record_id") else None,
        exam_attempt_id=to_int(payload.get("exam_attempt_id"), None)
        if payload.get("exam_attempt_id") else None,
        details=payload.get("details")
    )

    if not new_id:
        return {
            "success": False,
            "status_code": 500,
            "message": "Audit entry could not be recorded",
            "data": None
        }

    return {
        "success": True,
        "status_code": 201,
        "message": "Audit entry recorded",
        "data": {"audit_log_id": new_id}
    }
