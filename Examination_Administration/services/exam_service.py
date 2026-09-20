from Examination_Administration.repositories.exam_repository import ExamRepository
from Examination_Administration.models.exam_model import Exam

class ExamService:

    @staticmethod
    def create_exam(data, user_id):
        exam = Exam(
            SubjectID=data["SubjectID"],
            CreatedBy=user_id,
            ExamCode=data["ExamCode"],
            ExamTitle=data["ExamTitle"],
            ExamType=data["ExamType"],
            TotalMarks=data["TotalMarks"],
            PassingMarks=data["PassingMarks"],
            DurationMinutes=data["DurationMinutes"],
            Instructions=data.get("Instructions"),
            MaximumAttempts=data.get("MaximumAttempts", 1),
            ShuffleQuestions=data.get("ShuffleQuestions", True),
            ShuffleOptions=data.get("ShuffleOptions", True),
            NegativeMarking=data.get("NegativeMarking", False),
            NegativeMarksPerQuestion=data.get("NegativeMarksPerQuestion", 0)
        )

        return ExamRepository.create(exam)

    @staticmethod
    def get_all_exams():
        return ExamRepository.get_all()

    @staticmethod
    def get_exam(exam_id):
        return ExamRepository.get_by_id(exam_id)

    @staticmethod
    def update_exam(exam_id, data):
        exam = ExamRepository.get_by_id(exam_id)

        if not exam:
            return None

        allowed_fields = [
            "SubjectID",
            "ExamTitle",
            "ExamType",
            "TotalMarks",
            "PassingMarks",
            "DurationMinutes",
            "Instructions",
            "MaximumAttempts",
            "ShuffleQuestions",
            "ShuffleOptions",
            "NegativeMarking",
            "NegativeMarksPerQuestion"
        ]

        for field in allowed_fields:
            if field in data:
                setattr(exam, field, data[field])

        return ExamRepository.update(exam)

    @staticmethod
    def deactivate_exam(exam_id):
        exam = ExamRepository.get_by_id(exam_id)

        if not exam:
            return None

        return ExamRepository.deactivate(exam)