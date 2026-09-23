"""
Reporting & Analytics - HTTP layer.

Base path: /api/v1/reports
Access:    ADMIN and FACULTY.
"""

from flask import Blueprint, Response, request

from app.services import audit_service, reports_service
from app.utils.api_response import error_response, success_response
from app.utils.rbac import roles_required

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")


def _envelope(result):
    if result["success"]:
        return success_response(
            data=result.get("data"),
            message=result.get("message", "OK"),
            status_code=result.get("status_code", 200)
        )

    return error_response(
        message=result.get("message", "Request failed"),
        status_code=result.get("status_code", 400),
        errors=result.get("errors")
    )


@reports_bp.route("/overview", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def overview_route():
    """Platform-wide counters for dashboards."""
    return _envelope(reports_service.get_platform_overview())


@reports_bp.route("/exams", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def exam_catalogue_route():
    """Exams available for reporting. Filters: subject_id, status, created_by."""
    return _envelope(reports_service.list_exams(request.args))


@reports_bp.route("/exams/<int:exam_id>/summary", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def exam_summary_route(exam_id):
    return _envelope(reports_service.get_exam_summary(exam_id))


@reports_bp.route("/exams/<int:exam_id>/score-distribution", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def score_distribution_route(exam_id):
    return _envelope(reports_service.get_score_distribution(exam_id))


@reports_bp.route("/exams/<int:exam_id>/mastery", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def mastery_route(exam_id):
    return _envelope(reports_service.get_mastery_breakdown(exam_id))


@reports_bp.route("/exams/<int:exam_id>/item-analysis", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def item_analysis_route(exam_id):
    return _envelope(reports_service.get_item_analysis(exam_id))


@reports_bp.route("/exams/<int:exam_id>/full", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def full_report_route(exam_id):
    """Summary + distribution + mastery + item analysis in one round trip."""
    return _envelope(reports_service.get_full_exam_report(exam_id))


@reports_bp.route("/exams/<int:exam_id>/export", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def export_exam_report_route(exam_id):
    csv_text, filename = reports_service.export_exam_report_csv(exam_id)

    if csv_text is None:
        audit_service.record_event(
            module="Reporting", action="EXPORT", status="FAILED",
            entity_name="Exam", record_id=exam_id,
            details="Export requested for an exam that does not exist"
        )
        return error_response("Exam not found", status_code=404)

    # Exporting candidate data is a governance-relevant action, so the
    # Reporting module writes it to the audit ledger.
    audit_service.record_event(
        module="Reporting", action="EXPORT", status="SUCCESS",
        entity_name="Exam", record_id=exam_id,
        details="Exam analytics exported as {}".format(filename)
    )

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="{}"'.format(filename)
        }
    )


@reports_bp.route("/students/performance", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def student_performance_list_route():
    """FR-91. Filters: search, department_id, page, page_size."""
    return _envelope(reports_service.list_student_performance(request.args))


@reports_bp.route("/students/<int:student_id>/performance", methods=["GET"])
@roles_required("ADMIN", "FACULTY")
def student_performance_detail_route(student_id):
    return _envelope(reports_service.get_student_performance(student_id))
