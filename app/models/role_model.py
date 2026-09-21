from app.extensions import db


class Role(db.Model):
    __tablename__ = "Role"

    RoleID = db.Column(db.BigInteger, primary_key=True)
    RoleName = db.Column(db.String(30), unique=True, nullable=False)
    Description = db.Column(db.String(255))
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
