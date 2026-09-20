from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from Question_Management.services.question_service import QuestionService


question_bp = Blueprint(
    "question",
    __name__,
    url_prefix="/api/v1/questions"
)


@question_bp.route("", methods=["POST"])
@login_required
def create_question():

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can create questions"
        }), 403

    data = request.get_json()

    required_fields = [
        "SubjectID",
        "QuestionType",
        "QuestionText",
        "DefaultMarks",
        "DifficultyLevel"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        question = QuestionService.create_question(
            data,
            current_user.UserID
        )

        return jsonify({
            "success": True,
            "message": "Question created successfully",
            "question_id": question.QuestionID
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@question_bp.route("", methods=["GET"])
@login_required
def get_questions():

    questions = QuestionService.get_all_questions()

    result = []

    for question in questions:
        result.append({
            "QuestionID": question.QuestionID,
            "SubjectID": question.SubjectID,
            "CreatedBy": question.CreatedBy,
            "QuestionType": question.QuestionType,
            "QuestionText": question.QuestionText,
            "Explanation": question.Explanation,
            "DefaultMarks": float(question.DefaultMarks),
            "NegativeMarks": float(question.NegativeMarks or 0),
            "DifficultyLevel": question.DifficultyLevel,
            "IsActive": question.IsActive
        })

    return jsonify({
        "success": True,
        "questions": result
    })


@question_bp.route("/<int:question_id>", methods=["GET"])
@login_required
def get_question(question_id):

    question = QuestionService.get_question(question_id)

    if not question:
        return jsonify({
            "success": False,
            "message": "Question not found"
        }), 404

    return jsonify({
        "success": True,
        "question": {
            "QuestionID": question.QuestionID,
            "SubjectID": question.SubjectID,
            "CreatedBy": question.CreatedBy,
            "QuestionType": question.QuestionType,
            "QuestionText": question.QuestionText,
            "Explanation": question.Explanation,
            "DefaultMarks": float(question.DefaultMarks),
            "NegativeMarks": float(question.NegativeMarks or 0),
            "DifficultyLevel": question.DifficultyLevel,
            "IsActive": question.IsActive
        }
    })


@question_bp.route("/<int:question_id>", methods=["PUT"])
@login_required
def update_question(question_id):

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can update questions"
        }), 403

    data = request.get_json()

    question = QuestionService.update_question(
        question_id,
        data
    )

    if not question:
        return jsonify({
            "success": False,
            "message": "Question not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Question updated successfully"
    })


@question_bp.route("/<int:question_id>", methods=["DELETE"])
@login_required
def deactivate_question(question_id):

    if current_user.RoleID not in (1, 2):
        return jsonify({
            "success": False,
            "message": "Only Admin or Faculty can deactivate questions"
        }), 403

    question = QuestionService.deactivate_question(
        question_id
    )

    if not question:
        return jsonify({
            "success": False,
            "message": "Question not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Question deactivated successfully"
    })