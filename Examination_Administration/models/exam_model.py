from app.extensions import db


class Exam(db.Model):
    __tablename__ = "Exam"

    ExamID = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    SubjectID = db.Column(db.BigInteger, nullable=False)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    ExamCode = db.Column(db.String(30), unique=True, nullable=False)
    ExamTitle = db.Column(db.String(150), nullable=False)
    ExamType = db.Column(db.String(30), nullable=False)
    TotalMarks = db.Column(db.Numeric(6, 2), nullable=False)
    PassingMarks = db.Column(db.Numeric(6, 2), nullable=False)
    DurationMinutes = db.Column(db.Integer, nullable=False)
    Instructions = db.Column(db.Text)
    MaximumAttempts = db.Column(db.SmallInteger, nullable=False, default=1)
    ShuffleQuestions = db.Column(db.Boolean, default=True)
    ShuffleOptions = db.Column(db.Boolean, default=True)
    NegativeMarking = db.Column(db.Boolean, default=False)
    NegativeMarksPerQuestion = db.Column(db.Numeric(5, 2), default=0)
    ExamStatus = db.Column(db.Enum(
        "DRAFT",
        "SCHEDULED",
        "ACTIVE",
        "COMPLETED",
        "CANCELLED"
    ), nullable=False, default="DRAFT")
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, server_default=db.func.current_timestamp())