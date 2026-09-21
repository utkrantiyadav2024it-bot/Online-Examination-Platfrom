import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "insecure-default-key-replace-in-env")

    # Database Configuration
    # Supports DATABASE_URL directly (e.g. SQLite for tests/local, MySQL in prod)
    # or constructs MySQL URL from individual DB_* environment variables
    _database_url = os.getenv("DATABASE_URL")
    if _database_url:
        SQLALCHEMY_DATABASE_URI = _database_url
    elif os.getenv("DB_NAME"):
        SQLALCHEMY_DATABASE_URI = URL.create(
            "mysql+pymysql",
            username=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME"),
        )
    else:
        # Fallback local sqlite for development / testing when MySQL is not configured
        SQLALCHEMY_DATABASE_URI = "sqlite:///online_examination.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secure Session Management Configuration
    AUTH_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session_id")
    # Separate Flask's internal cookie from our stateful session_id cookie
    SESSION_COOKIE_NAME = "flask_session"
    SESSION_LIFETIME_MINUTES = int(os.getenv("SESSION_LIFETIME_MINUTES", "60"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_REFRESH_THRESHOLD_MINUTES = int(os.getenv("SESSION_REFRESH_THRESHOLD_MINUTES", "15"))
