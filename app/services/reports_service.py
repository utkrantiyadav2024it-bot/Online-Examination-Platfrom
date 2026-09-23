"""
Reporting & Analytics - business logic layer.

Covers FR-90 (exam-level analytics) and FR-91 (student performance reports).

Metric definitions used here
----------------------------
attendance_rate     submitted attempts / active registrations
pass_rate           results with PassStatus = 1 / total results
average_percentage  mean of Result.Percentage
median_percentage   middle value of the sorted percentages
std_deviation       population standard deviation of Result.Percentage
accuracy            correct answers / answers given (option-based items only)
discrimination      proportion correct in the top 27% of scorers minus the
                    proportion correct in the bottom 27% (Kelley's method).
                    >= 0.40 excellent, 0.30-0.39 good, 0.20-0.29 fair,
                    < 0.20 poor. Needs at least 8 scored attempts, otherwise
                    it is reported as null rather than as a misleading number.
"""

import csv
import io
import statistics
from datetime import datetime

from app.repositories import reports_repository as repo
from app.utils.api_response import iso, to_float, to_int

SCORE_BANDS = (
    ("81 - 100%", 81, 100),
    ("61 - 80%", 61, 80),
    ("41 - 60%", 41, 60),
    ("0 - 40%", 0, 40),
)

MIN_ATTEMPTS_FOR_DISCRIMINATION = 8
UPPER_LOWER_GROUP_RATIO = 0.27


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _percent(part, whole, digits=2):
    if not whole:
        return 0.0
    return round((part / whole) * 100, digits)


def _safe_round(value, digits=2):
    return round(float(value), digits) if value is not None else None


def _discrimination_label(index, auto_evaluated=True):
    if not auto_evaluated:
        return "Manual evaluation"
    if index is None:
        return "Not enough data"
    if index >= 0.40:
        return "Excellent"
    if index >= 0.30:
        return "Good"
    if index >= 0.20:
        return "Fair"
    return "Poor"


# ---------------------------------------------------------------------------
# Exam catalogue
# ---------------------------------------------------------------------------

def list_exams(args):
    rows = repo.fetch_exam_catalogue(
        subject_id=to_int(args.get("subject_id"), None) if args.get("subject_id") else None,
        status=(args.get("status") or "").strip() or None,
        created_by=to_int(args.get("created_by"), None) if args.get("created_by") else None,
    )

    items = [{
        "exam_id": row.get("exam_id"),
        "exam_code": row.get("exam_code"),
        "exam_title": row.get("exam_title"),
        "exam_type": row.get("exam_type"),
        "exam_status": row.get("exam_status"),
        "subject_id": row.get("subject_id"),
        "subject_code": row.get("subject_code"),
        "subject_name": row.get("subject_name"),
        "total_marks": to_float(row.get("total_marks")),
        "passing_marks": to_float(row.get("passing_marks")),
        "duration_minutes": to_int(row.get("duration_minutes")),
        "registered_count": to_int(row.get("registered_count")),
        "created_at": iso(row.get("created_at")),
    } for row in rows]

    return {
        "success": True,
        "status_code": 200,
        "message": "Exams retrieved",
        "data": {"items": items, "total": len(items)}
    }


# ---------------------------------------------------------------------------
# Exam summary (KPI cards)
# ---------------------------------------------------------------------------

def get_exam_summary(exam_id):
    exam = repo.fetch_exam(exam_id)

    if not exam:
        return {
            "success": False,
            "status_code": 404,
            "message": "Exam not found",
            "data": None
        }

    participation = repo.fetch_participation(exam_id)
    results = repo.fetch_exam_results(exam_id)

    registrations = participation["registrations"] or {}
    attempts = participation["attempts"] or {}

    active_registrations = to_int(registrations.get("active_registrations"))
    submitted_attempts = to_int(attempts.get("submitted_attempts"))

    percentages = [to_float(r.get("percentage")) for r in results]
    marks = [to_float(r.get("marks_obtained")) for r in results]
    pass_count = sum(1 for r in results if r.get("pass_status"))

    avg_time_seconds = to_float(attempts.get("avg_time_seconds"))

    data = {
        "exam": {
            "exam_id": exam.get("exam_id"),
            "exam_code": exam.get("exam_code"),
            "exam_title": exam.get("exam_title"),
            "exam_type": exam.get("exam_type"),
            "exam_status": exam.get("exam_status"),
            "subject_code": exam.get("subject_code"),
            "subject_name": exam.get("subject_name"),
            "total_marks": to_float(exam.get("total_marks")),
            "passing_marks": to_float(exam.get("passing_marks")),
            "duration_minutes": to_int(exam.get("duration_minutes")),
            "created_by_name": exam.get("created_by_name"),
        },
        "participation": {
            "total_registrations": to_int(registrations.get("total_registrations")),
            "active_registrations": active_registrations,
            "total_attempts": to_int(attempts.get("total_attempts")),
            "submitted_attempts": submitted_attempts,
            "in_progress_attempts": to_int(attempts.get("in_progress_attempts")),
            "auto_submitted": to_int(attempts.get("auto_submitted")),
            "attendance_rate": _percent(submitted_attempts, active_registrations),
        },
        "scores": {
            "evaluated_count": len(results),
            "pass_count": pass_count,
            "fail_count": len(results) - pass_count,
            "pass_rate": _percent(pass_count, len(results)),
            "average_percentage": _safe_round(statistics.fmean(percentages)) if percentages else 0.0,
            "median_percentage": _safe_round(statistics.median(percentages)) if percentages else 0.0,
            "highest_percentage": _safe_round(max(percentages)) if percentages else 0.0,
            "lowest_percentage": _safe_round(min(percentages)) if percentages else 0.0,
            "average_marks": _safe_round(statistics.fmean(marks)) if marks else 0.0,
            "highest_marks": _safe_round(max(marks)) if marks else 0.0,
            "lowest_marks": _safe_round(min(marks)) if marks else 0.0,
            "std_deviation": _safe_round(statistics.pstdev(percentages)) if len(percentages) > 1 else 0.0,
        },
        "timing": {
            "average_time_seconds": _safe_round(avg_time_seconds),
            "average_time_minutes": _safe_round(avg_time_seconds / 60 if avg_time_seconds else 0),
            "max_time_minutes": _safe_round(to_float(attempts.get("max_time_seconds")) / 60),
            "scheduled_duration_minutes": to_int(exam.get("duration_minutes")),
        }
    }

    schedule = repo.fetch_exam_schedule(exam_id)
    if schedule:
        data["schedule"] = {
            "start_time": iso(schedule.get("start_time")),
            "end_time": iso(schedule.get("end_time")),
            "schedule_status": schedule.get("schedule_status"),
        }

    return {
        "success": True,
        "status_code": 200,
        "message": "Exam summary retrieved",
        "data": data
    }


# ---------------------------------------------------------------------------
# Score distribution
# ---------------------------------------------------------------------------

def get_score_distribution(exam_id):
    exam = repo.fetch_exam(exam_id)

    if not exam:
        return {
            "success": False,
            "status_code": 404,
            "message": "Exam not found",
            "data": None
        }

    results = repo.fetch_exam_results(exam_id)
    percentages = [to_float(r.get("percentage")) for r in results]
    total = len(percentages)

    bands = []
    for label, low, high in SCORE_BANDS:
        count = sum(1 for p in percentages if low <= p <= high)
        bands.append({
            "label": label,
            "min_percentage": low,
            "max_percentage": high,
            "count": count,
            "share": _percent(count, total),
        })

    grades = {}
    for row in results:
        grade = row.get("grade") or "N/A"
        grades[grade] = grades.get(grade, 0) + 1

    return {
        "success": True,
        "status_code": 200,
        "message": "Score distribution retrieved",
        "data": {
            "total_evaluated": total,
            "bands": bands,
            "grades": [
                {"grade": g, "count": c, "share": _percent(c, total)}
                for g, c in sorted(grades.items())
            ],
            "highest_marks": _safe_round(max(
                [to_float(r.get("marks_obtained")) for r in results]
            )) if results else 0.0,
            "lowest_marks": _safe_round(min(
                [to_float(r.get("marks_obtained")) for r in results]
            )) if results else 0.0,
            "std_deviation": _safe_round(statistics.pstdev(percentages))
            if len(percentages) > 1 else 0.0,
            "exam_total_marks": to_float(exam.get("total_marks")),
        }
    }


# ---------------------------------------------------------------------------
# Item analysis
# ---------------------------------------------------------------------------

def _group_answers(answers):
    """question_id -> list of answer rows."""
    grouped = {}
    for row in answers:
        grouped.setdefault(row.get("question_id"), []).append(row)
    return grouped


def _score_by_attempt(results):
    return {
        row.get("attempt_id"): to_float(row.get("percentage"))
        for row in results
    }


def _discrimination_index(answer_rows, attempt_scores):
    """
    Kelley's upper/lower 27% discrimination index for one question.
    Returns None when the sample is too small to mean anything.
    """
    scored = [
        (attempt_scores[row.get("attempt_id")], row.get("is_correct"))
        for row in answer_rows
        if row.get("attempt_id") in attempt_scores
        and row.get("is_correct") is not None
    ]

    if len(scored) < MIN_ATTEMPTS_FOR_DISCRIMINATION:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)

    group_size = max(1, int(round(len(scored) * UPPER_LOWER_GROUP_RATIO)))
    upper = scored[:group_size]
    lower = scored[-group_size:]

    upper_correct = sum(1 for _, correct in upper if correct)
    lower_correct = sum(1 for _, correct in lower if correct)

    return round((upper_correct / len(upper)) - (lower_correct / len(lower)), 3)


def get_item_analysis(exam_id):
    exam = repo.fetch_exam(exam_id)

    if not exam:
        return {
            "success": False,
            "status_code": 404,
            "message": "Exam not found",
            "data": None
        }

    questions = repo.fetch_exam_questions(exam_id)
    answers = repo.fetch_exam_answers(exam_id)
    results = repo.fetch_exam_results(exam_id)

    grouped = _group_answers(answers)
    attempt_scores = _score_by_attempt(results)
    total_attempts = len(
        {row.get("attempt_id") for row in answers}
    ) or len(attempt_scores)

    items = []

    for question in questions:
        question_id = question.get("question_id")
        rows = grouped.get(question_id, [])

        auto_scored = [r for r in rows if r.get("is_correct") is not None]
        attempted = [r for r in rows if r.get("is_answered")]
        correct = sum(1 for r in auto_scored if r.get("is_correct"))
        incorrect = len(auto_scored) - correct
        skipped = max(total_attempts - len(attempted), 0)

        times = [
            to_int(r.get("time_spent_seconds"))
            for r in rows
            if to_int(r.get("time_spent_seconds")) > 0
        ]

        is_auto_evaluable = question.get("question_type") in (
            "MCQ", "MSQ", "TRUE_FALSE"
        )

        discrimination = (
            _discrimination_index(rows, attempt_scores)
            if is_auto_evaluable else None
        )

        items.append({
            "question_order": to_int(question.get("question_order")),
            "question_id": question_id,
            "question_text": question.get("question_text"),
            "question_type": question.get("question_type"),
            "difficulty_level": question.get("difficulty_level"),
            "marks": to_float(question.get("marks")),
            "auto_evaluated": is_auto_evaluable,
            "responses": len(rows),
            "attempted": len(attempted),
            "skipped": skipped,
            "correct_count": correct if is_auto_evaluable else None,
            "incorrect_count": incorrect if is_auto_evaluable else None,
            "correct_percentage": _percent(correct, len(auto_scored)) if is_auto_evaluable else None,
            "incorrect_percentage": _percent(incorrect, len(auto_scored)) if is_auto_evaluable else None,
            "facility_index": _safe_round(correct / len(auto_scored), 3) if auto_scored else None,
            "average_time_seconds": _safe_round(statistics.fmean(times)) if times else 0.0,
            "discrimination_index": discrimination,
            "discrimination_label": _discrimination_label(
                discrimination, is_auto_evaluable
            ),
        })

    return {
        "success": True,
        "status_code": 200,
        "message": "Item analysis retrieved",
        "data": {
            "total_questions": len(items),
            "total_attempts_considered": total_attempts,
            "min_attempts_for_discrimination": MIN_ATTEMPTS_FOR_DISCRIMINATION,
            "items": items
        }
    }


# ---------------------------------------------------------------------------
# Mastery breakdown
# ---------------------------------------------------------------------------

def get_mastery_breakdown(exam_id):
    """
    Accuracy grouped by difficulty level and by question type.

    The schema has no topic/category table, so difficulty and question type are
    the two dimensions that can be reported honestly from the current data.
    """
    exam = repo.fetch_exam(exam_id)

    if not exam:
        return {
            "success": False,
            "status_code": 404,
            "message": "Exam not found",
            "data": None
        }

    questions = {
        q.get("question_id"): q for q in repo.fetch_exam_questions(exam_id)
    }
    answers = repo.fetch_exam_answers(exam_id)

    by_difficulty = {}
    by_type = {}

    for row in answers:
        question = questions.get(row.get("question_id"))
        if not question:
            continue

        if row.get("is_correct") is None:
            continue

        difficulty = question.get("difficulty_level") or "UNSPECIFIED"
        qtype = question.get("question_type") or "UNSPECIFIED"

        for bucket, key in ((by_difficulty, difficulty), (by_type, qtype)):
            entry = bucket.setdefault(key, {"correct": 0, "total": 0})
            entry["total"] += 1
            if row.get("is_correct"):
                entry["correct"] += 1

    def _shape(bucket, key_name):
        return [{
            key_name: key,
            "correct": value["correct"],
            "responses": value["total"],
            "accuracy": _percent(value["correct"], value["total"]),
        } for key, value in sorted(bucket.items())]

    return {
        "success": True,
        "status_code": 200,
        "message": "Mastery breakdown retrieved",
        "data": {
            "dimension_note": (
                "Grouped by question difficulty and type; the schema has no "
                "topic/category dimension."
            ),
            "by_difficulty": _shape(by_difficulty, "difficulty_level"),
            "by_question_type": _shape(by_type, "question_type"),
        }
    }


# ---------------------------------------------------------------------------
# Combined payload (single call used by the report page)
# ---------------------------------------------------------------------------

def get_full_exam_report(exam_id):
    summary = get_exam_summary(exam_id)

    if not summary["success"]:
        return summary

    distribution = get_score_distribution(exam_id)
    mastery = get_mastery_breakdown(exam_id)
    items = get_item_analysis(exam_id)

    return {
        "success": True,
        "status_code": 200,
        "message": "Exam report retrieved",
        "data": {
            "summary": summary["data"],
            "score_distribution": distribution["data"],
            "mastery": mastery["data"],
            "item_analysis": items["data"],
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
    }


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def export_exam_report_csv(exam_id):
    report = get_full_exam_report(exam_id)

    if not report["success"]:
        return None, None

    data = report["data"]
    summary = data["summary"]
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Exam Analytics Report"])
    writer.writerow(["Exam Code", summary["exam"]["exam_code"]])
    writer.writerow(["Exam Title", summary["exam"]["exam_title"]])
    writer.writerow(["Subject", summary["exam"]["subject_name"]])
    writer.writerow(["Generated At", data["generated_at"]])
    writer.writerow([])

    writer.writerow(["Key Metrics"])
    writer.writerow(["Active Registrations", summary["participation"]["active_registrations"]])
    writer.writerow(["Submitted Attempts", summary["participation"]["submitted_attempts"]])
    writer.writerow(["Attendance Rate (%)", summary["participation"]["attendance_rate"]])
    writer.writerow(["Evaluated Results", summary["scores"]["evaluated_count"]])
    writer.writerow(["Pass Rate (%)", summary["scores"]["pass_rate"]])
    writer.writerow(["Average Percentage", summary["scores"]["average_percentage"]])
    writer.writerow(["Median Percentage", summary["scores"]["median_percentage"]])
    writer.writerow(["Standard Deviation", summary["scores"]["std_deviation"]])
    writer.writerow(["Average Time (minutes)", summary["timing"]["average_time_minutes"]])
    writer.writerow([])

    writer.writerow(["Score Distribution"])
    writer.writerow(["Band", "Count", "Share (%)"])
    for band in data["score_distribution"]["bands"]:
        writer.writerow([band["label"], band["count"], band["share"]])
    writer.writerow([])

    writer.writerow(["Item Analysis"])
    writer.writerow([
        "Q#", "Question", "Type", "Difficulty", "Correct %", "Incorrect %",
        "Avg Time (s)", "Discrimination Index", "Rating"
    ])
    for item in data["item_analysis"]["items"]:
        writer.writerow([
            item["question_order"],
            item["question_text"],
            item["question_type"],
            item["difficulty_level"],
            item["correct_percentage"],
            item["incorrect_percentage"],
            item["average_time_seconds"],
            item["discrimination_index"],
            item["discrimination_label"],
        ])

    filename = "exam_report_{}_{}.csv".format(
        summary["exam"]["exam_code"],
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    return buffer.getvalue(), filename


# ---------------------------------------------------------------------------
# Student performance (FR-91)
# ---------------------------------------------------------------------------

def list_student_performance(args):
    page = max(to_int(args.get("page"), 1) or 1, 1)
    page_size = min(max(to_int(args.get("page_size"), 25) or 25, 1), 200)
    search = (args.get("search") or "").strip() or None
    department_id = (
        to_int(args.get("department_id"), None)
        if args.get("department_id") else None
    )

    total = repo.count_students(search=search, department_id=department_id)
    rows = repo.fetch_student_performance(
        search=search,
        department_id=department_id,
        limit=page_size,
        offset=(page - 1) * page_size
    )

    items = [{
        "student_id": row.get("student_id"),
        "student_name": row.get("student_name"),
        "roll_number": row.get("roll_number"),
        "enrollment_number": row.get("enrollment_number"),
        "email": row.get("email"),
        "department_name": row.get("department_name"),
        "exams_attempted": to_int(row.get("exams_attempted")),
        "results_count": to_int(row.get("results_count")),
        "average_percentage": _safe_round(to_float(row.get("average_percentage"))),
        "highest_percentage": _safe_round(to_float(row.get("highest_percentage"))),
        "lowest_percentage": _safe_round(to_float(row.get("lowest_percentage"))),
        "pass_count": to_int(row.get("pass_count")),
        "fail_count": to_int(row.get("fail_count")),
    } for row in rows]

    total_pages = (total + page_size - 1) // page_size if total else 0

    return {
        "success": True,
        "status_code": 200,
        "message": "Student performance retrieved",
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total,
                "total_pages": total_pages,
                "has_previous": page > 1,
                "has_next": page < total_pages,
            }
        }
    }


def get_student_performance(student_id):
    profile = repo.fetch_student_profile(student_id)

    if not profile:
        return {
            "success": False,
            "status_code": 404,
            "message": "Student not found",
            "data": None
        }

    rows = repo.fetch_student_results(student_id)

    evaluated = [r for r in rows if r.get("percentage") is not None]
    percentages = [to_float(r.get("percentage")) for r in evaluated]
    pass_count = sum(1 for r in evaluated if r.get("pass_status"))

    return {
        "success": True,
        "status_code": 200,
        "message": "Student performance retrieved",
        "data": {
            "student": {
                "student_id": profile.get("student_id"),
                "student_name": profile.get("student_name"),
                "roll_number": profile.get("roll_number"),
                "enrollment_number": profile.get("enrollment_number"),
                "email": profile.get("email"),
                "department_name": profile.get("department_name"),
                "year": to_int(profile.get("year")),
                "semester": to_int(profile.get("semester")),
            },
            "aggregates": {
                "exams_registered": len(rows),
                "exams_evaluated": len(evaluated),
                "pass_count": pass_count,
                "fail_count": len(evaluated) - pass_count,
                "pass_rate": _percent(pass_count, len(evaluated)),
                "average_percentage": _safe_round(statistics.fmean(percentages)) if percentages else 0.0,
                "highest_percentage": _safe_round(max(percentages)) if percentages else 0.0,
                "lowest_percentage": _safe_round(min(percentages)) if percentages else 0.0,
            },
            "exams": [{
                "exam_id": r.get("exam_id"),
                "exam_code": r.get("exam_code"),
                "exam_title": r.get("exam_title"),
                "subject_name": r.get("subject_name"),
                "attempt_id": r.get("attempt_id"),
                "attempt_number": to_int(r.get("attempt_number")),
                "attempt_status": r.get("attempt_status"),
                "submitted_at": iso(r.get("submitted_at")),
                "total_marks": to_float(r.get("total_marks")),
                "marks_obtained": to_float(r.get("marks_obtained")) if r.get("marks_obtained") is not None else None,
                "percentage": _safe_round(to_float(r.get("percentage"))) if r.get("percentage") is not None else None,
                "grade": r.get("grade"),
                "pass_status": bool(r.get("pass_status")) if r.get("pass_status") is not None else None,
                "result_status": r.get("result_status"),
                "time_spent_minutes": _safe_round(to_int(r.get("time_spent_seconds")) / 60),
            } for r in rows]
        }
    }


# ---------------------------------------------------------------------------
# Platform overview
# ---------------------------------------------------------------------------

def get_platform_overview():
    data = repo.fetch_platform_overview()

    exams = data["exams"] or {}
    people = data["people"] or {}
    results = data["results"] or {}
    attempts = data["attempts"] or {}

    total_results = to_int(results.get("total_results"))
    pass_count = to_int(results.get("pass_count"))

    return {
        "success": True,
        "status_code": 200,
        "message": "Platform overview retrieved",
        "data": {
            "exams": {
                "total": to_int(exams.get("total_exams")),
                "active": to_int(exams.get("active_exams")),
                "scheduled": to_int(exams.get("scheduled_exams")),
                "completed": to_int(exams.get("completed_exams")),
            },
            "people": {
                "students": to_int(people.get("total_students")),
                "faculty": to_int(people.get("total_faculty")),
                "subjects": to_int(people.get("total_subjects")),
                "questions": to_int(people.get("total_questions")),
            },
            "attempts": {
                "total": to_int(attempts.get("total_attempts")),
                "in_progress": to_int(attempts.get("in_progress")),
            },
            "results": {
                "total": total_results,
                "published": to_int(results.get("published_count")),
                "pass_count": pass_count,
                "pass_rate": _percent(pass_count, total_results),
                "average_percentage": _safe_round(to_float(results.get("average_percentage"))),
            }
        }
    }
