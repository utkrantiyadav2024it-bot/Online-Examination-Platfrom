from datetime import datetime, timezone
from app.extensions import db


def utc_now() -> datetime:
    """Return current UTC time as an offset-naive datetime for universal DB compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserSession(db.Model):
    __tablename__ = "UserSession"

    SessionID = db.Column(db.String(128), primary_key=True)
    UserID = db.Column(
        db.BigInteger,
        db.ForeignKey("User.UserID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    IPAddress = db.Column(db.String(45), nullable=True)
    UserAgent = db.Column(db.String(255), nullable=True)
    CreatedAt = db.Column(db.DateTime, default=utc_now, nullable=False)
    LastActivityAt = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )
    ExpiresAt = db.Column(db.DateTime, nullable=False, index=True)
    IsRevoked = db.Column(db.Boolean, default=False, nullable=False, index=True)

    # Relationship back to User
    user = db.relationship("User", backref=db.backref("sessions", lazy=True, cascade="all, delete-orphan"))

    def is_expired(self) -> bool:
        """Check if session expiry has passed."""
        now = utc_now()
        expires = self.ExpiresAt
        if expires and expires.tzinfo is not None:
            expires = expires.replace(tzinfo=None)
        return now > expires if expires else True

    def is_valid(self) -> bool:
        """Check if session is currently active, unrevoked, and unexpired."""
        return not self.IsRevoked and not self.is_expired()

    def to_dict(self, include_user_details: bool = True) -> dict:
        """Return safe dictionary serialization (no passwords or secrets)."""
        data = {
            "session_id": self.SessionID,
            "user_id": self.UserID,
            "ip_address": self.IPAddress,
            "user_agent": self.UserAgent,
            "created_at": self.CreatedAt.isoformat() if self.CreatedAt else None,
            "last_activity_at": self.LastActivityAt.isoformat() if self.LastActivityAt else None,
            "expires_at": self.ExpiresAt.isoformat() if self.ExpiresAt else None,
            "is_revoked": self.IsRevoked,
            "is_expired": self.is_expired(),
            "is_valid": self.is_valid()
        }

        if include_user_details and self.user:
            data["user"] = {
                "user_id": self.user.UserID,
                "email": self.user.Email,
                "first_name": self.user.FirstName,
                "last_name": self.user.LastName,
                "role_id": self.user.RoleID,
                "is_active": self.user.IsActive
            }

        return data
