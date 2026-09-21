from datetime import datetime
from typing import List, Optional
from app.extensions import db
from Session_Management.models.session_model import UserSession, utc_now


class SessionRepository:

    @staticmethod
    def create(session: UserSession) -> UserSession:
        """Persist a new UserSession record."""
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
        return session

    @staticmethod
    def get_by_id(session_id: str) -> Optional[UserSession]:
        """Fetch session by its unique SessionID."""
        if not session_id:
            return None
        return db.session.get(UserSession, session_id)

    @staticmethod
    def get_active_by_user(user_id: int) -> List[UserSession]:
        """Fetch all non-revoked, non-expired sessions for a specific user."""
        now = utc_now()
        return (
            UserSession.query.filter(
                UserSession.UserID == user_id,
                UserSession.IsRevoked == False,
                UserSession.ExpiresAt > now
            )
            .order_by(UserSession.CreatedAt.desc())
            .all()
        )

    @staticmethod
    def get_all_active() -> List[UserSession]:
        """Fetch all currently active sessions across all users (for Admin dashboard)."""
        now = utc_now()
        return (
            UserSession.query.filter(
                UserSession.IsRevoked == False,
                UserSession.ExpiresAt > now
            )
            .order_by(UserSession.LastActivityAt.desc())
            .all()
        )

    @staticmethod
    def revoke(session_id: str) -> bool:
        """Mark a single session as revoked."""
        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False

        session.IsRevoked = True
        db.session.commit()
        return True

    @staticmethod
    def revoke_all_by_user(user_id: int, except_session_id: Optional[str] = None) -> int:
        """Revoke all active sessions for a user, optionally exempting the current session."""
        now = utc_now()
        query = UserSession.query.filter(
            UserSession.UserID == user_id,
            UserSession.IsRevoked == False,
            UserSession.ExpiresAt > now
        )
        if except_session_id:
            query = query.filter(UserSession.SessionID != except_session_id)

        sessions = query.all()
        count = len(sessions)
        for s in sessions:
            s.IsRevoked = True

        db.session.commit()
        return count

    @staticmethod
    def update_activity(session: UserSession, new_expires_at: Optional[datetime] = None) -> UserSession:
        """Update last activity and optionally extend expiration timestamp."""
        session.LastActivityAt = utc_now()
        if new_expires_at:
            if new_expires_at.tzinfo is not None:
                new_expires_at = new_expires_at.replace(tzinfo=None)
            session.ExpiresAt = new_expires_at
        db.session.commit()
        db.session.refresh(session)
        return session

    @staticmethod
    def cleanup_expired() -> int:
        """Mark past-due sessions as revoked."""
        now = utc_now()
        expired_sessions = UserSession.query.filter(
            UserSession.IsRevoked == False,
            UserSession.ExpiresAt <= now
        ).all()
        count = len(expired_sessions)
        for s in expired_sessions:
            s.IsRevoked = True
        db.session.commit()
        return count
