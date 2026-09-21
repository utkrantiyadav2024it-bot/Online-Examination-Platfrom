from Question_Management.repositories.question_repository import QuestionRepository
from Question_Management.models.question_model import Question


class QuestionService:

    @staticmethod
    def create_question(data, user_id):

        question = Question(
            SubjectID=data["SubjectID"],
            CreatedBy=user_id,
            QuestionType=data["QuestionType"],
            QuestionText=data["QuestionText"],
            Explanation=data.get("Explanation"),
            DefaultMarks=data["DefaultMarks"],
            NegativeMarks=data.get("NegativeMarks", 0),
            DifficultyLevel=data["DifficultyLevel"]
        )

        return QuestionRepository.create(question)

    @staticmethod
    def get_all_questions():
        return QuestionRepository.get_all()

    @staticmethod
    def get_question(question_id):
        return QuestionRepository.get_by_id(question_id)

    @staticmethod
    def update_question(question_id, data):

        question = QuestionRepository.get_by_id(question_id)

        if not question:
            return None

        allowed_fields = [
            "SubjectID",
            "QuestionType",
            "QuestionText",
            "Explanation",
            "DefaultMarks",
            "NegativeMarks",
            "DifficultyLevel"
        ]

        for field in allowed_fields:
            if field in data:
                setattr(question, field, data[field])

        return QuestionRepository.update(question)

    @staticmethod
    def deactivate_question(question_id):

        question = QuestionRepository.get_by_id(question_id)

        if not question:
            return None

        return QuestionRepository.deactivate(question)