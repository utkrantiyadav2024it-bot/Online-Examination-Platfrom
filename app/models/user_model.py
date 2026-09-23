from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "User"

    UserID = db.Column(db.BigInteger, primary_key=True)
    RoleID = db.Column(db.BigInteger, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Phone = db.Column(db.String(15), unique=True)
    PasswordHash = db.Column(db.String(255), nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    CreatedAt = db.Column(db.DateTime)
    UpdatedAt = db.Column(db.DateTime)

    def get_id(self):
        return str(self.UserID)
