"""
Audit Logging - data access layer (read side + generic write).

The existing app/repositories/audit_repository.py stays untouched: it is the
Authentication module's writer. This repository owns querying the ledger and
provides a module-agnostic writer used by audit_service.record_event().

All statements are parameterised text() queries, matching the style already
used in audit_repository.py.
"""

from app.extensions import db

_BASE_SELECT = """
    SELECT
        a.AuditLogID      AS audit_log_id,
        a.UserID          AS user_id,
        a.ExamAttemptID   AS exam_attempt_id,
        a.Module          AS module,
        a.Action          AS action,
        a.EntityName      AS entity_name,
        a.RecordID        AS record_id,
        a.Status          AS status,
        a.IPAddress       AS ip_address,
        a.Details         AS details,
        a.CreatedAt       AS created_at,
        u.FirstName       AS first_name,
        u.LastName        AS last_name,
        u.Email           AS email,
        r.RoleName        AS role_name
    FROM AuditLog a
    LEFT JOIN User u ON u.UserID = a.UserID
    LEFT JOIN Role r ON r.RoleID = u.RoleID
"""


def _build_filters(filters):
    """
    Turn a validated filter dict into a WHERE fragment + bind parameters.
    Returns (where_sql, params).
    """
    clauses = []
    params = {}

    if filters.get("module"):
        clauses.append("a.Module = :module")
        params["module"] = filters["module"]

    if filters.get("action"):
        clauses.append("a.Action = :action")
        params["action"] = filters["action"]

    if filters.get("status"):
        clauses.append("a.Status = :status")
        params["status"] = filters["status"]

    if filters.get("entity_name"):
        clauses.append("a.EntityName = :entity_name")
        params["entity_name"] = filters["entity_name"]

    if filters.get("user_id"):
        clauses.append("a.UserID = :user_id")
        params["user_id"] = filters["user_id"]

    if filters.get("exam_attempt_id"):
        clauses.append("a.ExamAttemptID = :exam_attempt_id")
        params["exam_attempt_id"] = filters["exam_attempt_id"]

    if filters.get("start_date"):
        clauses.append("a.CreatedAt >= :start_date")
        params["start_date"] = filters["start_date"]

    if filters.get("end_date"):
        clauses.append("a.CreatedAt <= :end_date")
        params["end_date"] = filters["end_date"]

    if filters.get("search"):
        clauses.append("""(
            a.Module     LIKE :search
            OR a.Action     LIKE :search
            OR a.Status     LIKE :search
            OR a.EntityName LIKE :search
            OR a.IPAddress  LIKE :search
            OR a.Details    LIKE :search
            OR u.FirstName  LIKE :search
            OR u.LastName   LIKE :search
            OR u.Email      LIKE :search
            OR CONCAT(u.FirstName, ' ', u.LastName) LIKE :search
        )""")
        params["search"] = "%{}%".format(filters["search"])

    where_sql = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params


def count_logs(filters):
    where_sql, params = _build_filters(filters)

    sql = """
        SELECT COUNT(*) AS total
        FROM AuditLog a
        LEFT JOIN User u ON u.UserID = a.UserID
    """ + where_sql

    row = db.session.execute(db.text(sql), params).first()
    return int(row.total) if row else 0


def fetch_logs(filters, limit, offset):
    where_sql, params = _build_filters(filters)
    params["limit"] = int(limit)
    params["offset"] = int(offset)

    sql = _BASE_SELECT + where_sql + """
        ORDER BY a.CreatedAt DESC, a.AuditLogID DESC
        LIMIT :limit OFFSET :offset
    """

    return db.session.execute(db.text(sql), params).mappings().all()


def fetch_log_by_id(audit_log_id):
    sql = _BASE_SELECT + " WHERE a.AuditLogID = :audit_log_id"
    return db.session.execute(
        db.text(sql), {"audit_log_id": audit_log_id}
    ).mappings().first()


def fetch_all_logs_for_export(filters, hard_limit=50000):
    """Same query as fetch_logs but without pagination (capped for safety)."""
    where_sql, params = _build_filters(filters)
    params["limit"] = int(hard_limit)

    sql = _BASE_SELECT + where_sql + """
        ORDER BY a.CreatedAt DESC, a.AuditLogID DESC
        LIMIT :limit
    """

    return db.session.execute(db.text(sql), params).mappings().all()


def fetch_distinct_values():
    """Distinct modules / actions / statuses, for populating filter dropdowns."""
    modules = db.session.execute(db.text(
        "SELECT DISTINCT Module FROM AuditLog WHERE Module IS NOT NULL ORDER BY Module"
    )).scalars().all()

    actions = db.session.execute(db.text(
        "SELECT DISTINCT Action FROM AuditLog WHERE Action IS NOT NULL ORDER BY Action"
    )).scalars().all()

    statuses = db.session.execute(db.text(
        "SELECT DISTINCT Status FROM AuditLog WHERE Status IS NOT NULL ORDER BY Status"
    )).scalars().all()

    return {
        "modules": list(modules),
        "actions": list(actions),
        "statuses": list(statuses)
    }


def fetch_summary():
    """Headline counters for the audit dashboard strip."""
    totals = db.session.execute(db.text("""
        SELECT
            COUNT(*)                                                      AS total_logs,
            SUM(CASE WHEN UPPER(Status) = 'SUCCESS' THEN 1 ELSE 0 END)    AS success_count,
            SUM(CASE WHEN UPPER(Status) <> 'SUCCESS' THEN 1 ELSE 0 END)   AS non_success_count,
            SUM(CASE WHEN CreatedAt >= (NOW() - INTERVAL 1 DAY) THEN 1 ELSE 0 END)
                                                                          AS last_24h_count,
            COUNT(DISTINCT UserID)                                        AS distinct_actors,
            MIN(CreatedAt)                                                AS first_log_at,
            MAX(CreatedAt)                                                AS last_log_at
        FROM AuditLog
    """)).mappings().first()

    by_module = db.session.execute(db.text("""
        SELECT Module AS module, COUNT(*) AS total
        FROM AuditLog
        GROUP BY Module
        ORDER BY total DESC
        LIMIT 10
    """)).mappings().all()

    by_action = db.session.execute(db.text("""
        SELECT Action AS action, COUNT(*) AS total
        FROM AuditLog
        GROUP BY Action
        ORDER BY total DESC
        LIMIT 10
    """)).mappings().all()

    return {
        "totals": totals,
        "by_module": by_module,
        "by_action": by_action
    }


def insert_log(
    user_id,
    module,
    action,
    status,
    entity_name=None,
    record_id=None,
    exam_attempt_id=None,
    ip_address=None,
    details=None
):
    """
    Module-agnostic append to the ledger.

    Deliberately INSERT-only: there is no update or delete path anywhere in
    this module, which is what keeps the trail append-only.
    """
    db.session.execute(
        db.text("""
            INSERT INTO AuditLog
                (UserID, ExamAttemptID, Module, Action, EntityName,
                 RecordID, Status, IPAddress, Details)
            VALUES
                (:user_id, :exam_attempt_id, :module, :action, :entity_name,
                 :record_id, :status, :ip_address, :details)
        """),
        {
            "user_id": user_id,
            "exam_attempt_id": exam_attempt_id,
            "module": module,
            "action": action,
            "entity_name": entity_name,
            "record_id": record_id,
            "status": status,
            "ip_address": ip_address,
            "details": details
        }
    )

    # Read the generated key on the same connection, before the commit
    # releases it back to the pool.
    row = db.session.execute(db.text("SELECT LAST_INSERT_ID() AS new_id")).first()
    new_id = int(row.new_id) if row and row.new_id else None

    db.session.commit()

    return new_id
