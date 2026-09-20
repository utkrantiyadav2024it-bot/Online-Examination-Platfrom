from app.models import User
from app.extensions import db

def get_user_by_email(email):
    return User.query.filter_by(Email=email).first()

def update_password(user, new_password_hash):
    user.PasswordHash = new_password_hash
    db.session.commit()
