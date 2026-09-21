-- Migration: 001_create_user_session.sql
-- Module: Secure Session Management (Kedar)
-- Purpose: Create UserSession table for server-side stateful session management, tracking active sessions,
--          preventing session fixation/hijacking, and supporting admin session revocation.

USE OnlineExaminationDB;

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

-- Indexes for high-performance session lookup and expiry cleanup
CREATE INDEX idx_session_user ON UserSession(UserID);
CREATE INDEX idx_session_expires ON UserSession(ExpiresAt);
CREATE INDEX idx_session_active ON UserSession(IsRevoked, ExpiresAt);
