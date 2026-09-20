from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from Examination_Administration.services.exam_service import ExamService

exam_bp = Blueprint(
    "exam",
    __name__,
    url_prefix="/api/v1/exams"
)


@exam_bp.route("", methods=["POST"])
@login_required
def create_exam():

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can create exams"
        }), 403

    data = request.get_json()

    required_fields = [
        "SubjectID",
        "ExamCode",
        "ExamTitle",
        "ExamType",
        "TotalMarks",
        "PassingMarks",
        "DurationMinutes"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        exam = ExamService.create_exam(
            data,
            current_user.UserID
        )

        return jsonify({
            "success": True,
            "message": "Exam created successfully",
            "exam_id": exam.ExamID
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@exam_bp.route("", methods=["GET"])
@login_required
def get_exams():

    exams = ExamService.get_all_exams()

    result = []

    for exam in exams:
        result.append({
            "ExamID": exam.ExamID,
            "SubjectID": exam.SubjectID,
            "ExamCode": exam.ExamCode,
            "ExamTitle": exam.ExamTitle,
            "ExamType": exam.ExamType,
            "TotalMarks": float(exam.TotalMarks),
            "PassingMarks": float(exam.PassingMarks),
            "DurationMinutes": exam.DurationMinutes,
            "ExamStatus": exam.ExamStatus,
            "IsActive": exam.IsActive
        })

    return jsonify({
        "success": True,
        "exams": result
    })


@exam_bp.route("/<int:exam_id>", methods=["GET"])
@login_required
def get_exam(exam_id):

    exam = ExamService.get_exam(exam_id)

    if not exam:
        return jsonify({
            "success": False,
            "message": "Exam not found"
        }), 404

    return jsonify({
        "success": True,
        "exam": {
            "ExamID": exam.ExamID,
            "SubjectID": exam.SubjectID,
            "CreatedBy": exam.CreatedBy,
            "ExamCode": exam.ExamCode,
            "ExamTitle": exam.ExamTitle,
            "ExamType": exam.ExamType,
            "TotalMarks": float(exam.TotalMarks),
            "PassingMarks": float(exam.PassingMarks),
            "DurationMinutes": exam.DurationMinutes,
            "Instructions": exam.Instructions,
            "MaximumAttempts": exam.MaximumAttempts,
            "ShuffleQuestions": exam.ShuffleQuestions,
            "ShuffleOptions": exam.ShuffleOptions,
            "NegativeMarking": exam.NegativeMarking,
            "NegativeMarksPerQuestion": float(
                exam.NegativeMarksPerQuestion or 0
            ),
            "ExamStatus": exam.ExamStatus,
            "IsActive": exam.IsActive
        }
    })


@exam_bp.route("/<int:exam_id>", methods=["PUT"])
@login_required
def update_exam(exam_id):

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can update exams"
        }), 403

    data = request.get_json()

    exam = ExamService.update_exam(exam_id, data)

    if not exam:
        return jsonify({
            "success": False,
            "message": "Exam not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Exam updated successfully"
    })


@exam_bp.route("/<int:exam_id>", methods=["DELETE"])
@login_required
def deactivate_exam(exam_id):

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can deactivate exams"
        }), 403

    exam = ExamService.deactivate_exam(exam_id)

    if not exam:
        return jsonify({
            "success": False,
            "message": "Exam not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Exam deactivated successfully"
    })