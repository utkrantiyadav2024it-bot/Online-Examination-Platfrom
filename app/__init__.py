from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models.user_model import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from Examination_Administration.routes.exam_routes import exam_bp
    app.register_blueprint(exam_bp)

    return app
