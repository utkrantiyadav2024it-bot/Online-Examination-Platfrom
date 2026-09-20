from app.extensions import db
from Examination_Administration.models.exam_model import Exam

class ExamRepository:

    @staticmethod
    def create(exam):
        db.session.add(exam)
        db.session.commit()
        db.session.refresh(exam)
        return exam

    @staticmethod
    def get_all():
        return Exam.query.filter_by(IsActive=True).all()

    @staticmethod
    def get_by_id(exam_id):
        return Exam.query.filter_by(
            ExamID=exam_id,
            IsActive=True
        ).first()

    @staticmethod
    def get_by_code(exam_code):
        return Exam.query.filter_by(
            ExamCode=exam_code
        ).first()

    @staticmethod
    def update(exam):
        db.session.commit()
        db.session.refresh(exam)
        return exam

    @staticmethod
    def deactivate(exam):
        exam.IsActive = False
        db.session.commit()
        return exam