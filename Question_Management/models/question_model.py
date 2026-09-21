from app.extensions import db


class Question(db.Model):
    __tablename__ = "Question"

    QuestionID = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    SubjectID = db.Column(
        db.BigInteger,
        nullable=False
    )

    CreatedBy = db.Column(
        db.BigInteger,
        nullable=False
    )

    QuestionType = db.Column(
        db.Enum(
            "MCQ",
            "MSQ",
            "TRUE_FALSE",
            "SHORT_ANSWER",
            "DESCRIPTIVE"
        ),
        nullable=False
    )

    QuestionText = db.Column(
        db.Text,
        nullable=False
    )

    Explanation = db.Column(
        db.Text
    )

    DefaultMarks = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    NegativeMarks = db.Column(
        db.Numeric(5, 2),
        default=0
    )

    DifficultyLevel = db.Column(
        db.Enum(
            "EASY",
            "MEDIUM",
            "HARD"
        ),
        nullable=False
    )

    IsActive = db.Column(
        db.Boolean,
        default=True
    )

    CreatedAt = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )