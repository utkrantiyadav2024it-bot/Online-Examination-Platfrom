from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

with app.app_context():
    users = db.session.execute(
        db.select(User)
    ).scalars().all()

    print("Database connection successful!")
    print("Number of users:", len(users))

    for user in users:
        print(user.UserID, user.Email, user.RoleID)
