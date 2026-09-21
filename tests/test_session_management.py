import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, Role
from Session_Management.models.session_model import UserSession
from Session_Management.services.session_service import SessionService
from Session_Management.repositories.session_repository import SessionRepository


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    AUTH_COOKIE_NAME = "session_id"
    SESSION_COOKIE_NAME = "flask_session"
    SESSION_LIFETIME_MINUTES = 60
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


@pytest.fixture
def test_app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        # Seed RBAC Roles
        admin_role = Role(RoleID=1, RoleName="ADMIN", Description="System Administrator", IsActive=True)
        faculty_role = Role(RoleID=2, RoleName="FACULTY", Description="Faculty/Examiner", IsActive=True)
        student_role = Role(RoleID=3, RoleName="STUDENT", Description="Student", IsActive=True)
        db.session.add_all([admin_role, faculty_role, student_role])

        # Seed Users
        admin_user = User(
            UserID=1,
            RoleID=1,
            FirstName="Admin",
            LastName="System",
            Email="admin@platform.com",
            PasswordHash=generate_password_hash("admin123"),
            IsActive=True
        )
        faculty_user = User(
            UserID=2,
            RoleID=2,
            FirstName="Rajesh",
            LastName="Sharma",
            Email="rajesh.sharma@college.edu",
            PasswordHash=generate_password_hash("faculty123"),
            IsActive=True
        )
        student_user = User(
            UserID=3,
            RoleID=3,
            FirstName="Rutuja",
            LastName="Ghodekar",
            Email="rutuja.student@college.edu",
            PasswordHash=generate_password_hash("student123"),
            IsActive=True
        )
        disabled_user = User(
            UserID=4,
            RoleID=3,
            FirstName="Disabled",
            LastName="User",
            Email="disabled@platform.com",
            PasswordHash=generate_password_hash("pass123"),
            IsActive=False
        )
        db.session.add_all([admin_user, faculty_user, student_user, disabled_user])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


# ============================================================================
# 1. Login & Session Creation Tests
# ============================================================================

def test_login_creates_secure_session_and_cookie(client, test_app):
    """Verify successful login creates database session and HttpOnly cookie."""
    response = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "session_id" in json_data["data"]
    session_id = json_data["data"]["session_id"]
    assert len(session_id) >= 32

    # Verify cookie presence and security flags
    cookies = response.headers.getlist("Set-Cookie")
    assert any("session_id=" in c for c in cookies)
    cookie_header = next(c for c in cookies if "session_id=" in c)
    assert "HttpOnly" in cookie_header
    assert "SameSite=Lax" in cookie_header

    # Verify session persisted in database
    with test_app.app_context():
        db_session = SessionRepository.get_by_id(session_id)
        assert db_session is not None
        assert db_session.UserID == 3
        assert db_session.IsRevoked is False
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        assert db_session.ExpiresAt > now_naive


def test_session_anti_fixation_on_login(client, test_app):
    """Verify that multiple logins produce distinct, fresh session tokens."""
    res1 = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    token1 = res1.get_json()["data"]["session_id"]

    res2 = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    token2 = res2.get_json()["data"]["session_id"]

    assert token1 != token2


def test_login_disabled_account_rejected(client):
    """Disabled accounts should not be permitted to create a session."""
    response = client.post("/api/v1/auth/login", json={
        "email": "disabled@platform.com",
        "password": "pass123"
    })
    assert response.status_code == 403
    json_data = response.get_json()
    assert json_data["success"] is False


def test_login_invalid_credentials(client):
    """Wrong password should return 401 and not issue a session."""
    response = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Set-Cookie" not in response.headers or not any("session_id=" in c and "Max-Age=0" not in c for c in response.headers.getlist("Set-Cookie"))


# ============================================================================
# 2. Session Validation & Protected Route Access Tests
# ============================================================================

def test_protected_api_access_with_session_cookie(client):
    """Authenticated user can access protected endpoints using the session cookie."""
    # Step 1: Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    assert login_res.status_code == 200

    # Step 2: Access protected /api/v1/sessions/current
    current_res = client.get("/api/v1/sessions/current")
    assert current_res.status_code == 200
    json_data = current_res.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["user"]["email"] == "rutuja.student@college.edu"
    assert json_data["data"]["user"]["role_id"] == 3


def test_protected_api_access_with_bearer_token(client):
    """Authenticated user can access protected endpoints using Authorization Bearer."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    session_id = login_res.get_json()["data"]["session_id"]

    # Clear test client cookies to test purely header-based auth
    client.delete_cookie("session_id")

    res = client.get(
        "/api/session/validate",
        headers={"Authorization": f"Bearer {session_id}"}
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["is_valid"] is True


def test_missing_session_returns_401(client):
    """Requests to protected endpoints with no session token must return 401."""
    client.delete_cookie("session_id")
    res = client.get("/api/v1/sessions/current")
    assert res.status_code == 401
    assert res.get_json()["errors"] == "MISSING_SESSION"


def test_invalid_session_returns_401(client):
    """Requests with forged or nonexistent session token must return 401."""
    client.delete_cookie("session_id")
    res = client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": "Bearer forged-non-existent-session-id"}
    )
    assert res.status_code == 401
    assert res.get_json()["errors"] == "INVALID_SESSION"


def test_expired_session_returns_401(client, test_app):
    """Past-due session must be rejected with 401 EXPIRED_SESSION."""
    client.delete_cookie("session_id")
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    with test_app.app_context():
        expired_session = UserSession(
            SessionID="expired-token-12345",
            UserID=3,
            CreatedAt=now_naive - timedelta(hours=2),
            LastActivityAt=now_naive - timedelta(hours=2),
            ExpiresAt=now_naive - timedelta(minutes=10),
            IsRevoked=False
        )
        db.session.add(expired_session)
        db.session.commit()

    res = client.get(
        "/api/session/validate",
        headers={"Authorization": "Bearer expired-token-12345"}
    )
    assert res.status_code == 401
    assert res.get_json()["errors"] == "EXPIRED_SESSION"


# ============================================================================
# 3. Logout & Session Destruction Tests
# ============================================================================

def test_logout_destroys_session_and_clears_cookie(client, test_app):
    """Logout must revoke session in DB, clear cookie, and reject subsequent calls."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    session_id = login_res.get_json()["data"]["session_id"]

    # Logout
    logout_res = client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # Verify session is revoked in database
    with test_app.app_context():
        db_session = SessionRepository.get_by_id(session_id)
        assert db_session.IsRevoked is True

    # Previously authenticated API must now fail with 401
    post_logout_res = client.get(
        "/api/v1/sessions/current",
        headers={"Authorization": f"Bearer {session_id}"}
    )
    assert post_logout_res.status_code == 401
    assert post_logout_res.get_json()["errors"] == "REVOKED_SESSION"


# ============================================================================
# 4. Session Refresh Tests
# ============================================================================

def test_session_refresh_extends_expiry(client, test_app):
    """Session refresh must extend expiration time."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    session_id = login_res.get_json()["data"]["session_id"]

    with test_app.app_context():
        orig_session = SessionRepository.get_by_id(session_id)
        orig_expiry = orig_session.ExpiresAt

    # Call refresh
    refresh_res = client.post("/api/session/refresh")
    assert refresh_res.status_code == 200
    new_expiry_str = refresh_res.get_json()["data"]["expires_at"]
    assert new_expiry_str is not None


# ============================================================================
# 5. Security & Sensitive Information Leakage Tests
# ============================================================================

def test_no_passwords_stored_or_leaked(client, test_app):
    """Verify passwords or password hashes are never present in session data or API responses."""
    login_res = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    session_id = login_res.get_json()["data"]["session_id"]

    # Check database model columns
    with test_app.app_context():
        db_session = SessionRepository.get_by_id(session_id)
        assert not hasattr(db_session, "password")
        assert not hasattr(db_session, "Password")
        assert not hasattr(db_session, "PasswordHash")
        session_dict = db_session.to_dict()
        assert "password" not in str(session_dict).lower()

    # Check API response
    api_res = client.get("/api/v1/sessions/current")
    json_text = api_res.get_data(as_text=True)
    assert "password" not in json_text.lower()


def test_role_based_route_protection(client):
    """Students cannot access Admin-only session listings."""
    # Student login
    client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })

    # Student attempts to list all active admin sessions -> 403 Forbidden
    admin_res = client.get("/api/v1/sessions")
    assert admin_res.status_code == 403


# ============================================================================
# 6. Admin Active Sessions Management Tests
# ============================================================================

def test_admin_can_list_and_terminate_sessions(client, test_app):
    """Admin can view all active sessions and forcibly terminate another user's session."""
    # 1. Student creates session
    stud_login = client.post("/api/v1/auth/login", json={
        "email": "rutuja.student@college.edu",
        "password": "student123"
    })
    stud_session_id = stud_login.get_json()["data"]["session_id"]

    # 2. Admin logs in
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@platform.com",
        "password": "admin123"
    })
    admin_session_id = admin_login.get_json()["data"]["session_id"]

    # 3. Admin lists sessions
    list_res = client.get("/api/v1/sessions")
    assert list_res.status_code == 200
    sessions_list = list_res.get_json()["data"]["sessions"]
    assert len(sessions_list) >= 2

    # 4. Admin terminates student session
    terminate_res = client.delete(f"/api/v1/sessions/{stud_session_id}")
    assert terminate_res.status_code == 200

    # 5. Student session is now revoked
    stud_verify = client.get(
        "/api/session/validate",
        headers={"Authorization": f"Bearer {stud_session_id}"}
    )
    assert stud_verify.status_code == 401


# ============================================================================
# 7. Dedicated Module Endpoint Tests (/api/session/*)
# ============================================================================

def test_dedicated_session_endpoints(client):
    """Verify dedicated endpoints: /api/session/create, /api/session/current, /api/session/logout."""
    # 1. Create session via POST /api/session/create
    create_res = client.post("/api/session/create", json={
        "email": "rajesh.sharma@college.edu",
        "password": "faculty123"
    })
    assert create_res.status_code == 201
    data = create_res.get_json()["data"]
    assert data["user"]["email"] == "rajesh.sharma@college.edu"
    assert data["user"]["role_id"] == 2
    session_id = data["session_id"]

    # 2. Retrieve current session via GET /api/session/current
    current_res = client.get("/api/session/current")
    assert current_res.status_code == 200
    assert current_res.get_json()["data"]["session_id"] == session_id

    # 3. Validate session via GET /api/session/validate
    val_res = client.get("/api/session/validate")
    assert val_res.status_code == 200
    assert val_res.get_json()["data"]["is_valid"] is True

    # 4. Refresh session via POST /api/session/refresh
    ref_res = client.post("/api/session/refresh")
    assert ref_res.status_code == 200

    # 5. Logout via POST /api/session/logout
    logout_res = client.post("/api/session/logout")
    assert logout_res.status_code == 200

    # 6. Verify subsequent call returns 401
    fail_res = client.get("/api/session/current")
    assert fail_res.status_code == 401
