from flask import request
from app.extensions import db


def create_audit_log(
    user_id,
    action,
    status,
    details=None,
    entity_name=None,
    record_id=None,
    module="Authentication"
):
    try:
        ip = "127.0.0.1"
        try:
            if request:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "127.0.0.1"
        except Exception:
            pass

        db.session.execute(
            db.text("""
                INSERT INTO AuditLog
                (
                    UserID,
                    Module,
                    Action,
                    EntityName,
                    RecordID,
                    Status,
                    IPAddress,
                    Details
                )
                VALUES
                (
                    :user_id,
                    :module,
                    :action,
                    :entity_name,
                    :record_id,
                    :status,
                    :ip_address,
                    :details
                )
            """),
            {
                "user_id": user_id,
                "module": module,
                "action": action,
                "entity_name": entity_name,
                "record_id": record_id,
                "status": status,
                "ip_address": ip,
                "details": details
            }
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Non-blocking audit log error
        pass
