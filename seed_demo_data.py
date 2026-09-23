"""
Optional demo-data seeder for the Reporting & Analytics and Audit Logging
modules.

    python seed_demo_data.py

Creates one department, one faculty, twelve students, one subject, one exam
with six questions, full attempt/answer/result data for every student, and a
handful of audit entries - enough for every metric on both pages to render.

Safe to skip entirely if you already have real data. Re-running it is a no-op
once the demo exam exists. It only INSERTs; nothing existing is modified.

Login accounts it creates (password for all three: Passw0rd!):
    admin@mmcoe.edu      ADMIN
    faculty@mmcoe.edu    FACULTY
    student1@mmcoe.edu   STUDENT   (through student12@mmcoe.edu)
"""

import random
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db

DEMO_EXAM_CODE = "EXAM-DBMS-MID"
PASSWORD = "Passw0rd!"

random.seed(7)


def scalar(sql, params=None):
    return db.session.execute(db.text(sql), params or {}).scalar()


def execute(sql, params=None):
    return db.session.execute(db.text(sql), params or {})


def last_id():
    return int(scalar("SELECT LAST_INSERT_ID()"))


def ensure_user(email, first, last, role_id, phone):
    existing = scalar(
        "SELECT UserID FROM User WHERE Email = :email", {"email": email}
    )
    if existing:
        return int(existing)

    execute("""
        INSERT INTO User (RoleID, FirstName, LastName, Email, Phone, PasswordHash, IsActive)
        VALUES (:role_id, :first, :last, :email, :phone, :hash, 1)
    """, {
        "role_id": role_id,
        "first": first,
        "last": last,
        "email": email,
        "phone": phone,
        "hash": generate_password_hash(PASSWORD),
    })
    return last_id()


QUESTIONS = [
    {
        "type": "MCQ",
        "text": "Which SQL clause is used to filter records in a SELECT statement?",
        "difficulty": "EASY",
        "marks": 16,
        "options": [("WHERE", True), ("HAVING", False), ("ORDER BY", False), ("GROUP BY", False)],
        "p_correct": 0.95,
    },
    {
        "type": "MSQ",
        "text": "Which of the following are ACID properties in DBMS?",
        "difficulty": "MEDIUM",
        "marks": 16,
        "options": [("Atomicity", True), ("Availability", False), ("Isolation", False), ("Scalability", False)],
        "p_correct": 0.80,
    },
    {
        "type": "MCQ",
        "text": "Which normal form eliminates transitive functional dependencies?",
        "difficulty": "MEDIUM",
        "marks": 16,
        "options": [("3NF", True), ("1NF", False), ("2NF", False), ("BCNF", False)],
        "p_correct": 0.70,
    },
    {
        "type": "TRUE_FALSE",
        "text": "A clustered index determines the physical order of rows in a table.",
        "difficulty": "EASY",
        "marks": 16,
        "options": [("True", True), ("False", False)],
        "p_correct": 0.85,
    },
    {
        "type": "MCQ",
        "text": "Which data structure is most commonly used to implement a database index?",
        "difficulty": "HARD",
        "marks": 16,
        "options": [("B+ Tree", True), ("Linked List", False), ("Stack", False), ("Heap file", False)],
        "p_correct": 0.55,
    },
    {
        "type": "DESCRIPTIVE",
        "text": "Explain the difference between optimistic and pessimistic concurrency control.",
        "difficulty": "HARD",
        "marks": 20,
        "options": [],
        "p_correct": None,
    },
]


def seed():
    app = create_app()

    with app.app_context():
        if scalar("SELECT ExamID FROM Exam WHERE ExamCode = :code", {"code": DEMO_EXAM_CODE}):
            print("Demo exam already present - nothing to do.")
            return

        # --- Department --------------------------------------------------
        dept_id = scalar(
            "SELECT DepartmentID FROM Department WHERE DepartmentCode = 'CSE'"
        )
        if not dept_id:
            execute("""
                INSERT INTO Department (DepartmentCode, DepartmentName, Description)
                VALUES ('CSE', 'Computer Engineering', 'Department of Computer Engineering')
            """)
            dept_id = last_id()

        # --- People ------------------------------------------------------
        admin_id = ensure_user("admin@mmcoe.edu", "System", "Administrator", 1, "9000000001")
        faculty_user_id = ensure_user("faculty@mmcoe.edu", "Rajesh", "Sharma", 2, "9000000002")

        if not scalar("SELECT FacultyID FROM Faculty WHERE UserID = :uid",
                      {"uid": faculty_user_id}):
            execute("""
                INSERT INTO Faculty (UserID, DepartmentID, EmployeeID, Designation)
                VALUES (:uid, :dept, 'EMP-1001', 'Associate Professor')
            """, {"uid": faculty_user_id, "dept": dept_id})

        student_ids = []
        for index in range(1, 13):
            user_id = ensure_user(
                "student{}@mmcoe.edu".format(index),
                "Student", "No{}".format(index), 3,
                "91000000{:02d}".format(index)
            )

            student_id = scalar("SELECT StudentID FROM Student WHERE UserID = :uid",
                                {"uid": user_id})
            if not student_id:
                execute("""
                    INSERT INTO Student
                        (UserID, DepartmentID, RollNumber, EnrollmentNumber, Year, Semester)
                    VALUES (:uid, :dept, :roll, :enroll, 3, 5)
                """, {
                    "uid": user_id,
                    "dept": dept_id,
                    "roll": "CSE-{:03d}".format(index),
                    "enroll": "ENR-2024-{:03d}".format(index),
                })
                student_id = last_id()

            student_ids.append(int(student_id))

        # --- Subject -----------------------------------------------------
        subject_id = scalar("SELECT SubjectID FROM Subject WHERE SubjectCode = 'CS301'")
        if not subject_id:
            execute("""
                INSERT INTO Subject
                    (DepartmentID, SubjectCode, SubjectName, Description, Credits, CreatedBy)
                VALUES (:dept, 'CS301', 'Database Management Systems',
                        'Relational databases, SQL and transactions', 4, :created_by)
            """, {"dept": dept_id, "created_by": faculty_user_id})
            subject_id = last_id()

        # --- Exam --------------------------------------------------------
        execute("""
            INSERT INTO Exam
                (SubjectID, CreatedBy, ExamCode, ExamTitle, ExamType, TotalMarks,
                 PassingMarks, DurationMinutes, Instructions, MaximumAttempts, ExamStatus)
            VALUES
                (:subject, :created_by, :code, 'DBMS Mid-Term Assessment', 'MID_TERM',
                 100, 40, 60, 'Answer all questions.', 1, 'COMPLETED')
        """, {"subject": subject_id, "created_by": faculty_user_id, "code": DEMO_EXAM_CODE})
        exam_id = last_id()

        start = datetime.now() - timedelta(days=2)
        execute("""
            INSERT INTO ExamSchedule (ExamID, StartTime, EndTime, ScheduleStatus)
            VALUES (:exam, :start, :end, 'COMPLETED')
        """, {"exam": exam_id, "start": start, "end": start + timedelta(minutes=60)})

        # --- Questions ---------------------------------------------------
        prepared = []
        for order, spec in enumerate(QUESTIONS, start=1):
            execute("""
                INSERT INTO Question
                    (SubjectID, CreatedBy, QuestionType, QuestionText, DefaultMarks,
                     DifficultyLevel)
                VALUES (:subject, :created_by, :qtype, :text, :marks, :difficulty)
            """, {
                "subject": subject_id,
                "created_by": faculty_user_id,
                "qtype": spec["type"],
                "text": spec["text"],
                "marks": spec["marks"],
                "difficulty": spec["difficulty"],
            })
            question_id = last_id()

            option_ids = []
            for option_order, (option_text, is_correct) in enumerate(spec["options"], start=1):
                execute("""
                    INSERT INTO QuestionOption (QuestionID, OptionText, OptionOrder, IsCorrect)
                    VALUES (:qid, :text, :ord, :correct)
                """, {
                    "qid": question_id,
                    "text": option_text,
                    "ord": option_order,
                    "correct": 1 if is_correct else 0,
                })
                option_ids.append((last_id(), is_correct))

            execute("""
                INSERT INTO ExamQuestion (ExamID, QuestionID, QuestionOrder, Marks)
                VALUES (:exam, :qid, :ord, :marks)
            """, {"exam": exam_id, "qid": question_id, "ord": order, "marks": spec["marks"]})

            prepared.append({
                "question_id": question_id,
                "spec": spec,
                "options": option_ids,
            })

        # --- Attempts, answers and results -------------------------------
        for position, student_id in enumerate(student_ids):
            # A little spread in ability so the analytics have signal.
            ability = 0.45 + (position / len(student_ids)) * 0.5

            execute("""
                INSERT INTO CandidateRegistration
                    (ExamID, StudentID, RegistrationStatus, EligibilityVerified)
                VALUES (:exam, :student, 'REGISTERED', 1)
            """, {"exam": exam_id, "student": student_id})
            registration_id = last_id()

            # One student registers but never shows up.
            if position == 0:
                continue

            time_spent = random.randint(1500, 3500)
            execute("""
                INSERT INTO ExamAttempt
                    (RegistrationID, AttemptNumber, StartTime, EndTime, SubmittedAt,
                     Status, TotalTimeSpentSeconds, IPAddress, SubmissionMethod)
                VALUES (:reg, 1, :start, :end, :end, 'EVALUATED', :time, :ip, 'MANUAL')
            """, {
                "reg": registration_id,
                "start": start,
                "end": start + timedelta(seconds=time_spent),
                "time": time_spent,
                "ip": "192.168.1.{}".format(40 + position),
            })
            attempt_id = last_id()

            obtained = 0.0
            correct_count = 0
            wrong_count = 0
            skipped_count = 0

            for item in prepared:
                spec = item["spec"]

                if spec["type"] == "DESCRIPTIVE":
                    awarded = round(spec["marks"] * random.uniform(0.4, 1.0), 2)
                    obtained += awarded
                    execute("""
                        INSERT INTO StudentAnswer
                            (AttemptID, QuestionID, AnswerText, IsAnswered, TimeSpentSeconds)
                        VALUES (:attempt, :qid, :text, 1, :time)
                    """, {
                        "attempt": attempt_id,
                        "qid": item["question_id"],
                        "text": "Optimistic control validates at commit time; "
                                "pessimistic control locks up front.",
                        "time": random.randint(90, 240),
                    })
                    continue

                # 8% chance the candidate skips the item entirely.
                if random.random() < 0.08:
                    skipped_count += 1
                    execute("""
                        INSERT INTO StudentAnswer
                            (AttemptID, QuestionID, IsAnswered, TimeSpentSeconds)
                        VALUES (:attempt, :qid, 0, :time)
                    """, {
                        "attempt": attempt_id,
                        "qid": item["question_id"],
                        "time": random.randint(5, 25),
                    })
                    continue

                got_it = random.random() < (spec["p_correct"] * ability + 0.15)
                pool = [oid for oid, correct in item["options"] if correct == got_it]
                if not pool:
                    pool = [item["options"][0][0]]
                selected = random.choice(pool)

                if got_it:
                    correct_count += 1
                    obtained += spec["marks"]
                else:
                    wrong_count += 1

                execute("""
                    INSERT INTO StudentAnswer
                        (AttemptID, QuestionID, SelectedOptionID, IsAnswered, TimeSpentSeconds)
                    VALUES (:attempt, :qid, :option, 1, :time)
                """, {
                    "attempt": attempt_id,
                    "qid": item["question_id"],
                    "option": selected,
                    "time": random.randint(20, 120),
                })

            percentage = round(obtained, 2)
            grade = ("A" if percentage >= 85 else
                     "B" if percentage >= 70 else
                     "C" if percentage >= 55 else
                     "D" if percentage >= 40 else "F")

            execute("""
                INSERT INTO Result
                    (AttemptID, TotalMarksObtained, Percentage, TotalCorrect, TotalWrong,
                     TotalSkipped, Grade, PassStatus, ResultStatus, PublishedAt, PublishedBy)
                VALUES
                    (:attempt, :marks, :pct, :correct, :wrong, :skipped, :grade,
                     :passed, 'PUBLISHED', NOW(), :publisher)
            """, {
                "attempt": attempt_id,
                "marks": round(obtained, 2),
                "pct": percentage,
                "correct": correct_count,
                "wrong": wrong_count,
                "skipped": skipped_count,
                "grade": grade,
                "passed": 1 if percentage >= 40 else 0,
                "publisher": faculty_user_id,
            })

        # --- Audit trail -------------------------------------------------
        audit_rows = [
            (admin_id, "Authentication", "LOGIN", "User", admin_id, "SUCCESS",
             "127.0.0.1", "Administrator signed in"),
            (faculty_user_id, "Authentication", "LOGIN", "User", faculty_user_id, "SUCCESS",
             "192.168.1.45", "Faculty signed in"),
            (faculty_user_id, "Exam", "CREATE", "Exam", exam_id, "SUCCESS",
             "192.168.1.45", "Created exam {}".format(DEMO_EXAM_CODE)),
            (faculty_user_id, "Evaluation", "PUBLISH", "Exam", exam_id, "SUCCESS",
             "192.168.1.45", "Results published for {}".format(DEMO_EXAM_CODE)),
            (None, "Authentication", "LOGIN", "User", None, "FAILED",
             "192.168.1.102", "Invalid email or password"),
            (admin_id, "RBAC", "UPDATE", "Role", 2, "SUCCESS",
             "127.0.0.1", "Granted PUBLISH_RESULT to FACULTY"),
            (admin_id, "Config", "UPDATE", "FeatureFlag", None, "SUCCESS",
             "127.0.0.1", "AUTO_EVALUATION_MSQ enabled"),
        ]

        for row in audit_rows:
            execute("""
                INSERT INTO AuditLog
                    (UserID, Module, Action, EntityName, RecordID, Status, IPAddress, Details)
                VALUES (:uid, :module, :action, :entity, :record, :status, :ip, :details)
            """, dict(zip(
                ["uid", "module", "action", "entity", "record", "status", "ip", "details"],
                row
            )))

        db.session.commit()

        print("Seed complete.")
        print("  Exam ID      :", exam_id)
        print("  Students     :", len(student_ids))
        print("  Admin login  : admin@mmcoe.edu /", PASSWORD)
        print("  Faculty login: faculty@mmcoe.edu /", PASSWORD)


if __name__ == "__main__":
    seed()
