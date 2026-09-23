# Reporting & Analytics + Audit Logging — Backend Reference

Both modules follow the layering already established by the Authentication
module: `routes → services → repositories → MySQL`, with the same JSON
envelope and the same Flask-Login session cookie.

```
{ "success": bool, "message": str, "data": object|null, "errors": object|null }
```

Authentication is the existing session cookie. Log in first via
`POST /api/v1/auth/login`; every endpoint below is session-protected.

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Audit entry created |
| 400 | Malformed request body |
| 401 | Not signed in / session expired |
| 403 | Signed in, but the role is not permitted |
| 404 | Exam, student or audit record not found |

---

## 1. Audit Logging — `/api/v1/audit`

**Role: ADMIN only.**

| Method | Path | Purpose |
|---|---|---|
| GET | `/logs` | Paginated, filterable trail |
| GET | `/logs/<id>` | One record |
| GET | `/filters` | Distinct modules / actions / statuses |
| GET | `/summary` | Counters for the dashboard strip |
| GET | `/logs/export` | CSV download (same filters as `/logs`) |
| POST | `/logs` | Append an entry (any signed-in role) |

### `GET /logs` query parameters

`search`, `module`, `action`, `status`, `entity_name`, `user_id`,
`exam_attempt_id`, `start_date`, `end_date`, `page`, `page_size`
(default 25, max 200).

`search` matches actor name, email, module, action, status, entity, IP and
details. Dates accept `YYYY-MM-DD` or a full timestamp; a bare `end_date` is
widened to 23:59:59 of that day.

```json
{
  "data": {
    "items": [{
      "audit_log_id": 1005, "created_at": "2026-09-20T14:48:02",
      "actor_name": "Rajesh Sharma", "actor_email": "faculty@mmcoe.edu",
      "actor_role": "FACULTY", "module": "Evaluation", "action": "PUBLISH",
      "entity_name": "Exam", "record_id": 12, "target": "Exam #12",
      "status": "SUCCESS", "ip_address": "192.168.1.45",
      "details": "Results published", "exam_attempt_id": null
    }],
    "pagination": {
      "page": 1, "page_size": 25, "total_records": 57, "total_pages": 3,
      "has_previous": false, "has_next": true
    }
  }
}
```

### `POST /logs`

Requires a CSRF token from `GET /api/v1/auth/csrf-token` in the `X-CSRFToken`
header.

```json
{ "module": "ExamMonitoring", "action": "TAB_SWITCH", "status": "FLAGGED",
  "entity_name": "ExamAttempt", "record_id": 44, "details": "Focus lost 3 times" }
```

### Recording events from other modules

Import the service function rather than writing SQL:

```python
from app.services.audit_service import record_event

record_event("Evaluation", "PUBLISH", "SUCCESS",
             entity_name="Exam", record_id=exam_id,
             details="Results published")
```

Actor and IP default to the current session and request. The call never
raises — a failed audit write will not break the operation that triggered it.

The ledger is append-only by construction: the repository exposes `insert_log`
and read queries only. There is no UPDATE or DELETE path anywhere in the
module.

---

## 2. Reporting & Analytics — `/api/v1/reports`

**Roles: ADMIN and FACULTY.**

| Method | Path | Purpose |
|---|---|---|
| GET | `/overview` | Platform-wide counters |
| GET | `/exams` | Exam catalogue (drives the selector) |
| GET | `/exams/<id>/summary` | KPI block |
| GET | `/exams/<id>/score-distribution` | Bands + grade spread |
| GET | `/exams/<id>/mastery` | Accuracy by difficulty and question type |
| GET | `/exams/<id>/item-analysis` | Per-question psychometrics |
| GET | `/exams/<id>/full` | All four in one round trip |
| GET | `/exams/<id>/export` | CSV download |
| GET | `/students/performance` | FR-91 list (`search`, `department_id`, paging) |
| GET | `/students/<id>/performance` | One student, exam by exam |

### Metric definitions

| Metric | Definition |
|---|---|
| `attendance_rate` | submitted attempts ÷ active registrations |
| `pass_rate` | results with `PassStatus = 1` ÷ total results |
| `average_percentage` | mean of `Result.Percentage` |
| `median_percentage` | middle value of the sorted percentages |
| `std_deviation` | population standard deviation of the percentages |
| `correct_percentage` | correct ÷ auto-scored responses for that question |
| `facility_index` | the same ratio as a 0–1 value (item difficulty) |
| `discrimination_index` | Kelley's method: proportion correct in the top 27% of scorers minus the proportion correct in the bottom 27% |

Discrimination rating: ≥ 0.40 excellent, 0.30–0.39 good, 0.20–0.29 fair,
below 0.20 poor. With fewer than 8 scored attempts the value is returned as
`null` rather than as a number that would be statistically meaningless.

### Auto-evaluated vs manually evaluated items

Correctness is derived from `QuestionOption.IsCorrect` for the selected
option, so it is only defined for `MCQ`, `MSQ` and `TRUE_FALSE`. Items of type
`SHORT_ANSWER` and `DESCRIPTIVE` return `auto_evaluated: false` with null
accuracy and a `Manual evaluation` label, and they are excluded from the
mastery breakdown. They still report response counts and average time.

### Why "mastery" is by difficulty and type

The frontend mock showed a topic/curriculum breakdown, but `schema.sql` has no
topic or category table — `Question` carries `SubjectID`, `QuestionType` and
`DifficultyLevel` only, and an exam belongs to a single subject. The endpoint
therefore reports the two dimensions the data actually supports and the page
heading was changed to match. If a `QuestionCategory` table is added later,
`get_mastery_breakdown()` is the only function that needs to change.

---

## 3. Frontend wiring

| Page | Controller | Endpoints used |
|---|---|---|
| `/admin/audit/list.html` | `static/js/audit_logs.js` | `/audit/logs`, `/filters`, `/summary`, `/logs/export` |
| `/reports/exam_report.html` | `static/js/reports.js` | `/reports/exams`, `/exams/<id>/full`, `/exams/<id>/export` |

Both controllers use `fetch(..., { credentials: 'same-origin' })`, escape every
value before inserting it into the DOM, show a spinner while loading, and
render an inline banner with a sign-in link on 401/403 instead of failing
silently.

---

## 4. Files

New:

```
app/utils/__init__.py
app/utils/api_response.py            envelope + Decimal/datetime helpers
app/utils/rbac.py                    roles_required decorator
app/repositories/audit_log_repository.py
app/repositories/reports_repository.py
app/services/audit_service.py
app/services/reports_service.py
app/routes/audit_routes.py
app/routes/reports_routes.py
static/js/audit_logs.js
static/js/reports.js
run.py                               full-stack entry point
seed_demo_data.py                    optional demo data
requirements.txt
.env.example
docs/reporting_audit_api.md
```

Modified (frontend wiring for these two modules only):

```
templates/admin/audit/list.html
templates/reports/exam_report.html
```

Unchanged: `app.py`, `app/__init__.py`, `app/config.py`, `app/extensions.py`,
all models, `auth_repository.py`, `audit_repository.py`, `auth_service.py`,
`auth_routes.py`, `schema.sql`, and every other template.

`run.py` registers the two blueprints on the application returned by
`create_app()`, which is why `app/__init__.py` did not need to change. If you
would rather register them centrally later, add these two lines to
`create_app()` and drop them from `run.py`:

```python
from app.routes.audit_routes import audit_bp
from app.routes.reports_routes import reports_bp
app.register_blueprint(audit_bp)
app.register_blueprint(reports_bp)
```
