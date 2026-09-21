from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    import os
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # API endpoints should return JSON 401 when unauthorized
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            "success": False,
            "message": "Authentication required. Please sign in.",
            "data": None,
            "errors": "UNAUTHORIZED"
        }), 401

    from app.models.user_model import User
    from app.models.role_model import Role
    from app.models.audit_model import AuditLog
    from Session_Management.models.session_model import UserSession

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from Examination_Administration.routes.exam_routes import exam_bp
    app.register_blueprint(exam_bp)

    from Question_Management.routes.question_routes import question_bp
    app.register_blueprint(question_bp)

    from Session_Management.routes.session_routes import session_bp
    app.register_blueprint(session_bp)

    return app
