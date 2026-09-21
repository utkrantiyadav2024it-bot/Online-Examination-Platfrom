import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from flask import request as flask_request, session as flask_session
from app.config import Config
from app.repositories.audit_repository import create_audit_log
from Session_Management.models.session_model import UserSession, utc_now
from Session_Management.repositories.session_repository import SessionRepository


class SessionService:

    @staticmethod
    def generate_session_token() -> str:
        """Generate a cryptographically secure, unpredictable 64-character token."""
        return secrets.token_urlsafe(48)

    @staticmethod
    def extract_client_ip(req=None) -> str:
        """Extract client IP address, respecting reverse proxy headers."""
        req = req or flask_request
        if not req:
            return "127.0.0.1"

        forwarded = req.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return req.remote_addr or "127.0.0.1"

    @staticmethod
    def extract_user_agent(req=None) -> str:
        """Extract client User-Agent string truncated to 255 chars."""
        req = req or flask_request
        if not req:
            return "Unknown"
        ua = req.headers.get("User-Agent", "Unknown")
        return ua[:255] if ua else "Unknown"

    @classmethod
    def create_session(cls, user, req=None) -> UserSession:
        """
        Create a new secure session after successful authentication.
        Enforces session fixation protection by generating a fresh token.
        """
        # Session Fixation Prevention: Clear any previous session state in Flask session
        try:
            flask_session.clear()
            flask_session["_auth_user_id"] = user.UserID
        except Exception:
            pass

        token = cls.generate_session_token()
        now = utc_now()
        lifetime = timedelta(minutes=Config.SESSION_LIFETIME_MINUTES)
        expires_at = now + lifetime

        ip_addr = cls.extract_client_ip(req)
        user_agent = cls.extract_user_agent(req)

        user_session = UserSession(
            SessionID=token,
            UserID=user.UserID,
            IPAddress=ip_addr,
            UserAgent=user_agent,
            CreatedAt=now,
            LastActivityAt=now,
            ExpiresAt=expires_at,
            IsRevoked=False
        )

        created = SessionRepository.create(user_session)

        # Audit session creation
        create_audit_log(
            user_id=user.UserID,
            action="SESSION_CREATE",
            status="SUCCESS",
            details=f"Session created. Expires at {expires_at.isoformat()}",
            entity_name="UserSession",
            record_id=user.UserID,
            module="SessionManagement"
        )

        return created

    @classmethod
    def validate_session(cls, session_id: str, req=None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate session existence, revocation status, expiration, and hijacking indicators.
        Returns (is_valid, payload_or_error_info).
        """
        if not session_id:
            return False, {
                "error": "MISSING_SESSION",
                "message": "Authentication required. Missing session token."
            }

        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False, {
                "error": "INVALID_SESSION",
                "message": "Session is invalid or does not exist."
            }

        if session.IsRevoked:
            return False, {
                "error": "REVOKED_SESSION",
                "message": "Session has been invalidated/logged out."
            }

        if session.is_expired():
            session.IsRevoked = True
            SessionRepository.create(session)
            return False, {
                "error": "EXPIRED_SESSION",
                "message": "Session has expired. Please sign in again."
            }

        # Check for potential session hijacking (User-Agent mismatch)
        req = req or flask_request
        if req:
            current_ua = cls.extract_user_agent(req)
            if session.UserAgent and session.UserAgent != "Unknown" and current_ua != "Unknown":
                if session.UserAgent != current_ua:
                    create_audit_log(
                        user_id=session.UserID,
                        action="SESSION_HIJACK_ATTEMPT",
                        status="WARNING",
                        details=f"User-Agent mismatch: stored='{session.UserAgent}', received='{current_ua}'",
                        entity_name="UserSession",
                        record_id=session.UserID,
                        module="SessionManagement"
                    )

        # Sliding window / activity update
        SessionRepository.update_activity(session)

        return True, {
            "session": session,
            "user": session.user
        }

    @classmethod
    def refresh_session(cls, session_id: str, req=None) -> Tuple[bool, Dict[str, Any]]:
        """Extend the lifetime of an active session."""
        is_valid, result = cls.validate_session(session_id, req)
        if not is_valid:
            return False, result

        session: UserSession = result["session"]
        new_expires_at = utc_now() + timedelta(minutes=Config.SESSION_LIFETIME_MINUTES)
        SessionRepository.update_activity(session, new_expires_at=new_expires_at)

        create_audit_log(
            user_id=session.UserID,
            action="SESSION_REFRESH",
            status="SUCCESS",
            details=f"Session extended until {new_expires_at.isoformat()}",
            entity_name="UserSession",
            record_id=session.UserID,
            module="SessionManagement"
        )

        return True, {
            "session_id": session.SessionID,
            "expires_at": new_expires_at.isoformat(),
            "user_id": session.UserID
        }

    @classmethod
    def destroy_session(cls, session_id: str) -> bool:
        """Securely destroy/revoke a session on logout."""
        if not session_id:
            return False

        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False

        user_id = session.UserID
        success = SessionRepository.revoke(session_id)

        try:
            flask_session.clear()
        except Exception:
            pass

        if success:
            create_audit_log(
                user_id=user_id,
                action="LOGOUT",
                status="SUCCESS",
                details="Session destroyed upon user logout",
                entity_name="UserSession",
                record_id=user_id,
                module="SessionManagement"
            )

        return success

    @classmethod
    def list_active_sessions(cls) -> list:
        """List active sessions for admin monitoring (no passwords or sensitive data)."""
        active_sessions = SessionRepository.get_all_active()
        return [s.to_dict(include_user_details=True) for s in active_sessions]

    @classmethod
    def force_terminate_session(cls, session_id: str, admin_user_id: Optional[int] = None) -> bool:
        """Admin action to forcibly terminate a specific active session."""
        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False

        success = SessionRepository.revoke(session_id)
        if success:
            create_audit_log(
                user_id=admin_user_id,
                action="ADMIN_TERMINATE_SESSION",
                status="SUCCESS",
                details=f"Admin {admin_user_id} revoked session {session_id} for user {session.UserID}",
                entity_name="UserSession",
                record_id=session.UserID,
                module="SessionManagement"
            )
        return success
