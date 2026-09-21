# Online Examination Platform

## Secure Session Management Module

**Author / Assigned Backend Engineer:** Kedar  
**Module:** Secure Session Management  
**Architecture:** Python 3.14+, Flask 3.1, SQLAlchemy 2.0, Flask-Login, PyMySQL / SQLite, Pytest

---

## 1. Module Overview

The **Secure Session Management** module provides server-side, stateful session handling and lifecycle management for the Online Examination Platform. It prevents session fixation, session hijacking, credential replay, and unauthorized API access while exposing administrative session monitoring and force revocation controls.

### Key Capabilities:
- **Cryptographic Session Identifiers:** Generated using 48 bytes of cryptographically secure random entropy (`secrets.token_urlsafe(48)`), yielding 64-character URL-safe tokens with 384 bits of entropy.
- **Anti-Session Fixation:** Previous session data and tokens are automatically destroyed upon successful credential verification; a completely new session ID is generated and bound to the authenticated user.
- **Session Hijacking Defense:** Binds client IP addresses and User-Agent signatures upon session creation and audits anomalies on subsequent requests.
- **Hardened Cookie Policy:**
  - `HttpOnly`: Prevents client-side scripts from accessing cookies (mitigating XSS theft).
  - `SameSite=Lax`: Prevents cross-site request forgery attacks during third-party requests.
  - `Secure`: Enforced in production environments over HTTPS.
  - Explicit `Max-Age` / `Expires`: Coordinated with server-side database expiration timestamps.
- **Multi-Channel Authentication:** Accepts tokens via either secure HttpOnly cookies (browser requests) or `Authorization: Bearer <session_id>` / `X-Session-ID` headers (REST API clients).
- **Session Timeout & Invalidation:** Supports absolute timeout and idle activity tracking. Revoked and expired sessions return HTTP `401 Unauthorized`.
- **Zero Sensitive Data Exposure:** Password hashes, salts, and secrets are strictly excluded from session database records and API responses.
- **Admin Session Management:** Enables administrators to inspect active sessions in real time and immediately invalidate compromised or duplicate sessions.

---

## 2. Authentication & Session Conceptual Flow

```
User Login Request
        │  (POST /api/v1/auth/login or POST /api/session/create)
        ▼
Credential Verification
        │  (Verify Argon2id / werkzeug password hash against User table)
        ▼
Credentials Valid
        │
        ├── Clear / Regenerate Session (Anti-Fixation)
        ├── Generate Cryptographic Token (`secrets.token_urlsafe(48)`)
        ├── Record `UserSession` in Database (UserID, IP, UserAgent, ExpiresAt)
        ├── Log Audit Entry (`AuditLog`: Action = 'SESSION_CREATE', Status = 'SUCCESS')
        ▼
Set Secure Cookie & Return Response
        │  (Set-Cookie: session_id=...; HttpOnly; SameSite=Lax; Path=/)
        ▼
Authenticated API Request
        │  (Client sends Cookie or `Authorization: Bearer <session_id>`)
        ▼
Session Middleware (`@require_session`)
        │
        ├── Extract Token (Bearer Header > X-Session-ID > Cookie)
        ├── Check `UserSession` in DB (Exists, `IsRevoked == False`, `ExpiresAt > UTC_NOW`)
        ├── Verify Client Binding (IP / User-Agent hijacking check)
        ├── Slide Activity Window (`LastActivityAt = UTC_NOW`)
        ├── Populate `g.current_user` and `g.current_session`
        ├── Enforce RBAC Role permissions if specified
        ▼
Execute Protected Controller / API
```

---

## 3. API Endpoints

### Authentication & Core Session APIs

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Public | Authenticates credentials, creates a secure session, sets HttpOnly cookie |
| `POST` | `/api/session/create` | Public | Dedicated session creation endpoint (accepts email & password) |
| `GET` | `/api/v1/auth/session` | `@require_session` | Returns current user identity and session validity |
| `GET` | `/api/v1/sessions/current` | `@require_session` | Returns detailed current session metadata and user info |
| `GET` | `/api/session/current` | `@require_session` | Alias for current session retrieval |
| `GET` | `/api/v1/sessions/validate` | `@require_session` | Validates session health and unexpired status |
| `GET` | `/api/session/validate` | `@require_session` | Alias for session validation |
| `POST` | `/api/v1/sessions/refresh` | `@require_session` | Extends session expiration by configured lifetime and updates cookie |
| `POST` | `/api/session/refresh` | `@require_session` | Alias for session refresh |
| `POST` | `/api/v1/auth/logout` | Session / Cookie | Revokes session in DB, destroys Flask session, clears cookie |
| `POST` | `/api/session/logout` | `@require_session` | Dedicated session logout endpoint |

### Administrative Session APIs

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/sessions` | `@require_session(allowed_roles=[1])` | Lists all active user sessions across the system |
| `GET` | `/api/sessions` | `@require_session(allowed_roles=[1])` | Alias for active sessions list |
| `DELETE` | `/api/v1/sessions/<sessionId>` | `@require_session` | Forcibly terminates session (Admin or Session Owner) |
| `DELETE` | `/api/sessions/<sessionId>` | `@require_session` | Alias for session termination |

---

## 4. Middleware Usage Guide

Protect any route or blueprint using the `@require_session` decorator:

```python
from flask import Blueprint, jsonify, g
from Session_Management.middleware import require_session

example_bp = Blueprint("example", __name__)

# Basic authentication (any valid active session)
@example_bp.route("/api/v1/student/data", methods=["GET"])
@require_session
def get_student_data():
    user = g.current_user
    session = g.current_session
    return jsonify({"user_id": user.UserID, "email": user.Email})

# Role-Based Access Control (Admin or Faculty only)
@example_bp.route("/api/v1/exams/publish", methods=["POST"])
@require_session(allowed_roles=[1, 2])
def publish_exam():
    return jsonify({"success": True, "message": "Exam published"})
```

---

## 5. Database Changes

### Table: `UserSession`
Created via migration script: `migrations/001_create_user_session.sql` and incorporated into `schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS UserSession (
    SessionID VARCHAR(128) PRIMARY KEY,
    UserID BIGINT NOT NULL,
    IPAddress VARCHAR(45) NULL,
    UserAgent VARCHAR(255) NULL,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LastActivityAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ExpiresAt DATETIME NOT NULL,
    IsRevoked BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_session_user
        FOREIGN KEY (UserID) REFERENCES User(UserID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_session_user ON UserSession(UserID);
CREATE INDEX idx_session_expires ON UserSession(ExpiresAt);
CREATE INDEX idx_session_active ON UserSession(IsRevoked, ExpiresAt);
```

---

## 6. Environment Configuration

Copy `.env.example` to `.env` and set environment-specific values:

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | *(Required in prod)* | Application secret key used for CSRF and signing |
| `DATABASE_URL` | *(Optional)* | Direct SQLAlchemy connection URI (e.g. SQLite for testing) |
| `DB_HOST` | `localhost` | MySQL Host |
| `DB_PORT` | `3306` | MySQL Port |
| `DB_USER` | `root` | MySQL Username |
| `DB_PASSWORD` | `""` | MySQL Password |
| `DB_NAME` | `OnlineExaminationDB` | MySQL Database Name |
| `SESSION_COOKIE_NAME` | `session_id` | Name of the HttpOnly session cookie |
| `SESSION_LIFETIME_MINUTES` | `60` | Server-side session duration in minutes |
| `SESSION_COOKIE_SECURE` | `False` | Enforce HTTPS only on session cookies (`True` in production) |
| `SESSION_COOKIE_SAMESITE` | `Lax` | SameSite cookie policy |
| `SESSION_REFRESH_THRESHOLD_MINUTES` | `15` | Minimum time window for sliding session refresh |

---

## 7. How to Run and Test

### 1. Setup Virtual Environment & Dependencies
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
pytest -v tests/test_session_management.py
```

### 3. Run the Development Server
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
