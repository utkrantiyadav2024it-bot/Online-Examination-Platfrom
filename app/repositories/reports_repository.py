"""
Reporting & Analytics - data access layer.

Raw parameterised SQL against the schema in schema.sql. Nothing here computes
statistics; the repository returns rows and the service derives the metrics,
which keeps the heavy maths testable without a database round-trip.
"""

from app.extensions import db


# ---------------------------------------------------------------------------
# Exam catalogue
# ---------------------------------------------------------------------------

def fetch_exam_catalogue(subject_id=None, status=None, created_by=None):
    """Exams available for reporting, newest first (drives the exam selector)."""
    clauses = ["1 = 1"]
    params = {}

    if subject_id:
        clauses.append("e.SubjectID = :subject_id")
        params["subject_id"] = subject_id

    if status:
        clauses.append("e.ExamStatus = :status")
        params["status"] = status

    if created_by:
        clauses.append("e.CreatedBy = :created_by")
        params["created_by"] = created_by

    sql = """
        SELECT
            e.ExamID        AS exam_id,
            e.ExamCode      AS exam_code,
            e.ExamTitle     AS exam_title,
            e.ExamType      AS exam_type,
            e.ExamStatus    AS exam_status,
            e.TotalMarks    AS total_marks,
            e.PassingMarks  AS passing_marks,
            e.DurationMinutes AS duration_minutes,
            e.CreatedAt     AS created_at,
            s.SubjectID     AS subject_id,
            s.SubjectCode   AS subject_code,
            s.SubjectName   AS subject_name,
            (
                SELECT COUNT(*)
                FROM CandidateRegistration cr
                WHERE cr.ExamID = e.ExamID
                  AND cr.RegistrationStatus = 'REGISTERED'
            ) AS registered_count
        FROM Exam e
        JOIN Subject s ON s.SubjectID = e.SubjectID
        WHERE """ + " AND ".join(clauses) + """
        ORDER BY e.CreatedAt DESC, e.ExamID DESC
    """

    return db.session.execute(db.text(sql), params).mappings().all()


def fetch_exam(exam_id):
    sql = """
        SELECT
            e.ExamID          AS exam_id,
            e.ExamCode        AS exam_code,
            e.ExamTitle       AS exam_title,
            e.ExamType        AS exam_type,
            e.ExamStatus      AS exam_status,
            e.TotalMarks      AS total_marks,
            e.PassingMarks    AS passing_marks,
            e.DurationMinutes AS duration_minutes,
            e.NegativeMarking AS negative_marking,
            e.CreatedBy       AS created_by,
            e.CreatedAt       AS created_at,
            s.SubjectID       AS subject_id,
            s.SubjectCode     AS subject_code,
            s.SubjectName     AS subject_name,
            CONCAT(u.FirstName, ' ', u.LastName) AS created_by_name
        FROM Exam e
        JOIN Subject s ON s.SubjectID = e.SubjectID
        LEFT JOIN User u ON u.UserID = e.CreatedBy
        WHERE e.ExamID = :exam_id
    """

    return db.session.execute(
        db.text(sql), {"exam_id": exam_id}
    ).mappings().first()


def fetch_exam_schedule(exam_id):
    sql = """
        SELECT
            ScheduleID     AS schedule_id,
            StartTime      AS start_time,
            EndTime        AS end_time,
            ScheduleStatus AS schedule_status
        FROM ExamSchedule
        WHERE ExamID = :exam_id
        ORDER BY StartTime DESC
        LIMIT 1
    """

    return db.session.execute(
        db.text(sql), {"exam_id": exam_id}
    ).mappings().first()


# ---------------------------------------------------------------------------
# Participation
# ---------------------------------------------------------------------------

def fetch_participation(exam_id):
    """Registration and attempt counters for one exam."""
    registrations = db.session.execute(db.text("""
        SELECT
            COUNT(*) AS total_registrations,
            SUM(CASE WHEN RegistrationStatus = 'REGISTERED' THEN 1 ELSE 0 END)
                AS active_registrations
        FROM CandidateRegistration
        WHERE ExamID = :exam_id
    """), {"exam_id": exam_id}).mappings().first()

    attempts = db.session.execute(db.text("""
        SELECT
            COUNT(ea.AttemptID) AS total_attempts,
            SUM(CASE WHEN ea.Status IN ('SUBMITTED', 'AUTO_SUBMITTED', 'EVALUATED')
                     THEN 1 ELSE 0 END)                           AS submitted_attempts,
            SUM(CASE WHEN ea.Status = 'IN_PROGRESS' THEN 1 ELSE 0 END)
                                                                  AS in_progress_attempts,
            SUM(CASE WHEN ea.AutoSubmitted = 1 THEN 1 ELSE 0 END) AS auto_submitted,
            AVG(NULLIF(ea.TotalTimeSpentSeconds, 0))              AS avg_time_seconds,
            MAX(ea.TotalTimeSpentSeconds)                         AS max_time_seconds
        FROM CandidateRegistration cr
        JOIN ExamAttempt ea ON ea.RegistrationID = cr.RegistrationID
        WHERE cr.ExamID = :exam_id
    """), {"exam_id": exam_id}).mappings().first()

    return {"registrations": registrations, "attempts": attempts}


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def fetch_exam_results(exam_id):
    """One row per evaluated attempt, used for every score-based metric."""
    sql = """
        SELECT
            r.ResultID           AS result_id,
            r.AttemptID          AS attempt_id,
            r.TotalMarksObtained AS marks_obtained,
            r.Percentage         AS percentage,
            r.TotalCorrect       AS total_correct,
            r.TotalWrong         AS total_wrong,
            r.TotalSkipped       AS total_skipped,
            r.Grade              AS grade,
            r.PassStatus         AS pass_status,
            r.ResultStatus       AS result_status,
            ea.TotalTimeSpentSeconds AS time_spent_seconds,
            st.StudentID         AS student_id,
            st.RollNumber        AS roll_number,
            CONCAT(u.FirstName, ' ', u.LastName) AS student_name
        FROM Result r
        JOIN ExamAttempt ea ON ea.AttemptID = r.AttemptID
        JOIN CandidateRegistration cr ON cr.RegistrationID = ea.RegistrationID
        JOIN Student st ON st.StudentID = cr.StudentID
        JOIN User u ON u.UserID = st.UserID
        WHERE cr.ExamID = :exam_id
        ORDER BY r.TotalMarksObtained DESC
    """

    return db.session.execute(
        db.text(sql), {"exam_id": exam_id}
    ).mappings().all()


# ---------------------------------------------------------------------------
# Item analysis
# ---------------------------------------------------------------------------

def fetch_exam_questions(exam_id):
    sql = """
        SELECT
            eq.ExamQuestionID  AS exam_question_id,
            eq.QuestionOrder   AS question_order,
            eq.Marks           AS marks,
            eq.NegativeMarks   AS negative_marks,
            q.QuestionID       AS question_id,
            q.QuestionText     AS question_text,
            q.QuestionType     AS question_type,
            q.DifficultyLevel  AS difficulty_level
        FROM ExamQuestion eq
        JOIN Question q ON q.QuestionID = eq.QuestionID
        WHERE eq.ExamID = :exam_id
        ORDER BY eq.QuestionOrder
    """

    return db.session.execute(
        db.text(sql), {"exam_id": exam_id}
    ).mappings().all()


def fetch_exam_answers(exam_id):
    """
    Every submitted answer for the exam, with auto-evaluated correctness.

    Correctness is derived from the selected option's IsCorrect flag, so it is
    only meaningful for option-based question types. Descriptive and
    short-answer items carry is_correct = NULL and are reported separately as
    "manually evaluated".
    """
    sql = """
        SELECT
            sa.AttemptID        AS attempt_id,
            sa.QuestionID       AS question_id,
            sa.SelectedOptionID AS selected_option_id,
            sa.AnswerText       AS answer_text,
            sa.IsAnswered       AS is_answered,
            sa.IsMarkedForReview AS is_marked_for_review,
            sa.TimeSpentSeconds AS time_spent_seconds,
            q.QuestionType      AS question_type,
            CASE
                WHEN q.QuestionType IN ('MCQ', 'MSQ', 'TRUE_FALSE')
                     AND sa.SelectedOptionID IS NOT NULL
                THEN CASE WHEN qo.IsCorrect = 1 THEN 1 ELSE 0 END
                ELSE NULL
            END AS is_correct
        FROM StudentAnswer sa
        JOIN ExamAttempt ea ON ea.AttemptID = sa.AttemptID
        JOIN CandidateRegistration cr ON cr.RegistrationID = ea.RegistrationID
        JOIN Question q ON q.QuestionID = sa.QuestionID
        LEFT JOIN QuestionOption qo ON qo.OptionID = sa.SelectedOptionID
        WHERE cr.ExamID = :exam_id
    """

    return db.session.execute(
        db.text(sql), {"exam_id": exam_id}
    ).mappings().all()


# ---------------------------------------------------------------------------
# Student performance
# ---------------------------------------------------------------------------

def fetch_student_performance(search=None, department_id=None,
                              limit=50, offset=0):
    clauses = ["1 = 1"]
    params = {"limit": int(limit), "offset": int(offset)}

    if search:
        clauses.append("""(
            u.FirstName LIKE :search
            OR u.LastName LIKE :search
            OR u.Email LIKE :search
            OR st.RollNumber LIKE :search
            OR st.EnrollmentNumber LIKE :search
        )""")
        params["search"] = "%{}%".format(search)

    if department_id:
        clauses.append("st.DepartmentID = :department_id")
        params["department_id"] = department_id

    where_sql = " AND ".join(clauses)

    sql = """
        SELECT
            st.StudentID        AS student_id,
            st.RollNumber       AS roll_number,
            st.EnrollmentNumber AS enrollment_number,
            CONCAT(u.FirstName, ' ', u.LastName) AS student_name,
            u.Email             AS email,
            d.DepartmentName    AS department_name,
            COUNT(DISTINCT ea.AttemptID)                 AS exams_attempted,
            COUNT(DISTINCT r.ResultID)                   AS results_count,
            COALESCE(AVG(r.Percentage), 0)               AS average_percentage,
            COALESCE(MAX(r.Percentage), 0)               AS highest_percentage,
            COALESCE(MIN(r.Percentage), 0)               AS lowest_percentage,
            COALESCE(SUM(CASE WHEN r.PassStatus = 1 THEN 1 ELSE 0 END), 0) AS pass_count,
            COALESCE(SUM(CASE WHEN r.ResultID IS NOT NULL AND r.PassStatus = 0
                              THEN 1 ELSE 0 END), 0)     AS fail_count
        FROM Student st
        JOIN User u ON u.UserID = st.UserID
        JOIN Department d ON d.DepartmentID = st.DepartmentID
        LEFT JOIN CandidateRegistration cr ON cr.StudentID = st.StudentID
        LEFT JOIN ExamAttempt ea ON ea.RegistrationID = cr.RegistrationID
        LEFT JOIN Result r ON r.AttemptID = ea.AttemptID
        WHERE """ + where_sql + """
        GROUP BY
            st.StudentID, st.RollNumber, st.EnrollmentNumber,
            u.FirstName, u.LastName, u.Email, d.DepartmentName
        ORDER BY average_percentage DESC, student_name ASC
        LIMIT :limit OFFSET :offset
    """

    return db.session.execute(db.text(sql), params).mappings().all()


def count_students(search=None, department_id=None):
    clauses = ["1 = 1"]
    params = {}

    if search:
        clauses.append("""(
            u.FirstName LIKE :search
            OR u.LastName LIKE :search
            OR u.Email LIKE :search
            OR st.RollNumber LIKE :search
            OR st.EnrollmentNumber LIKE :search
        )""")
        params["search"] = "%{}%".format(search)

    if department_id:
        clauses.append("st.DepartmentID = :department_id")
        params["department_id"] = department_id

    sql = """
        SELECT COUNT(*) AS total
        FROM Student st
        JOIN User u ON u.UserID = st.UserID
        WHERE """ + " AND ".join(clauses)

    row = db.session.execute(db.text(sql), params).first()
    return int(row.total) if row else 0


def fetch_student_profile(student_id):
    sql = """
        SELECT
            st.StudentID        AS student_id,
            st.RollNumber       AS roll_number,
            st.EnrollmentNumber AS enrollment_number,
            st.Year             AS year,
            st.Semester         AS semester,
            CONCAT(u.FirstName, ' ', u.LastName) AS student_name,
            u.Email             AS email,
            d.DepartmentName    AS department_name
        FROM Student st
        JOIN User u ON u.UserID = st.UserID
        JOIN Department d ON d.DepartmentID = st.DepartmentID
        WHERE st.StudentID = :student_id
    """

    return db.session.execute(
        db.text(sql), {"student_id": student_id}
    ).mappings().first()


def fetch_student_results(student_id):
    sql = """
        SELECT
            e.ExamID             AS exam_id,
            e.ExamCode           AS exam_code,
            e.ExamTitle          AS exam_title,
            e.TotalMarks         AS total_marks,
            s.SubjectName        AS subject_name,
            ea.AttemptID         AS attempt_id,
            ea.AttemptNumber     AS attempt_number,
            ea.Status            AS attempt_status,
            ea.SubmittedAt       AS submitted_at,
            ea.TotalTimeSpentSeconds AS time_spent_seconds,
            r.TotalMarksObtained AS marks_obtained,
            r.Percentage         AS percentage,
            r.Grade              AS grade,
            r.PassStatus         AS pass_status,
            r.ResultStatus       AS result_status
        FROM CandidateRegistration cr
        JOIN Exam e ON e.ExamID = cr.ExamID
        JOIN Subject s ON s.SubjectID = e.SubjectID
        LEFT JOIN ExamAttempt ea ON ea.RegistrationID = cr.RegistrationID
        LEFT JOIN Result r ON r.AttemptID = ea.AttemptID
        WHERE cr.StudentID = :student_id
        ORDER BY ea.SubmittedAt DESC, e.ExamID DESC
    """

    return db.session.execute(
        db.text(sql), {"student_id": student_id}
    ).mappings().all()


# ---------------------------------------------------------------------------
# Platform overview
# ---------------------------------------------------------------------------

def fetch_platform_overview():
    exams = db.session.execute(db.text("""
        SELECT
            COUNT(*) AS total_exams,
            SUM(CASE WHEN ExamStatus = 'ACTIVE' THEN 1 ELSE 0 END)    AS active_exams,
            SUM(CASE WHEN ExamStatus = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_exams,
            SUM(CASE WHEN ExamStatus = 'SCHEDULED' THEN 1 ELSE 0 END) AS scheduled_exams
        FROM Exam
    """)).mappings().first()

    people = db.session.execute(db.text("""
        SELECT
            (SELECT COUNT(*) FROM Student WHERE IsActive = 1) AS total_students,
            (SELECT COUNT(*) FROM Faculty WHERE IsActive = 1) AS total_faculty,
            (SELECT COUNT(*) FROM Subject WHERE IsActive = 1) AS total_subjects,
            (SELECT COUNT(*) FROM Question WHERE IsActive = 1) AS total_questions
    """)).mappings().first()

    results = db.session.execute(db.text("""
        SELECT
            COUNT(*)                        AS total_results,
            COALESCE(AVG(Percentage), 0)    AS average_percentage,
            SUM(CASE WHEN PassStatus = 1 THEN 1 ELSE 0 END)          AS pass_count,
            SUM(CASE WHEN ResultStatus = 'PUBLISHED' THEN 1 ELSE 0 END)
                                            AS published_count
        FROM Result
    """)).mappings().first()

    attempts = db.session.execute(db.text("""
        SELECT
            COUNT(*) AS total_attempts,
            SUM(CASE WHEN Status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress
        FROM ExamAttempt
    """)).mappings().first()

    return {
        "exams": exams,
        "people": people,
        "results": results,
        "attempts": attempts
    }
