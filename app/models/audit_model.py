from datetime import datetime, timezone
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "AuditLog"

    AuditLogID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    UserID = db.Column(db.BigInteger, nullable=True)
    ExamAttemptID = db.Column(db.BigInteger, nullable=True)
    Module = db.Column(db.String(50), nullable=False)
    Action = db.Column(db.String(50), nullable=False)
    EntityName = db.Column(db.String(50), nullable=True)
    RecordID = db.Column(db.BigInteger, nullable=True)
    Status = db.Column(db.String(20), nullable=False)
    IPAddress = db.Column(db.String(45), nullable=True)
    Details = db.Column(db.Text, nullable=True)
    CreatedAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
