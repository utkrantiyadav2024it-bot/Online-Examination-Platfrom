from flask import request

from app.extensions import db
from app.models import User


def create_audit_log(
    user_id,
    action,
    status,
    details=None,
    entity_name=None,
    record_id=None
):
    audit_log = db.session.execute(
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
            "module": "Authentication",
            "action": action,
            "entity_name": entity_name,
            "record_id": record_id,
            "status": status,
            "ip_address": request.remote_addr,
            "details": details
        }
    )

    db.session.commit()
