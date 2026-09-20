from app.extensions import db
from Question_Management.models.question_model import Question


class QuestionRepository:

    @staticmethod
    def create(question):
        db.session.add(question)
        db.session.commit()
        db.session.refresh(question)
        return question

    @staticmethod
    def get_all():
        return Question.query.filter_by(IsActive=True).all()

    @staticmethod
    def get_by_id(question_id):
        return Question.query.filter_by(
            QuestionID=question_id,
            IsActive=True
        ).first()

    @staticmethod
    def update(question):
        db.session.commit()
        db.session.refresh(question)
        return question

    @staticmethod
    def deactivate(question):
        question.IsActive = False
        db.session.commit()
        return question