"""
Full-stack entry point for the Online Examination Platform.

    python run.py

What this does that app.py does not:
  * builds the real application through app.create_app() (database, session,
    CSRF, Authentication API)
  * registers the Reporting & Analytics and Audit Logging blueprints
  * serves the existing Jinja templates from the same origin, so the pages and
    the APIs share one session cookie and fetch() needs no CORS setup

app.py is left exactly as it was: it is still the template-only preview server.
Nothing else in the project was modified to make this file work.
"""

import os

from flask import abort, render_template
from jinja2 import FileSystemLoader

from app import create_app
from app.routes.audit_routes import audit_bp
from app.routes.reports_routes import reports_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


def build_app():
    application = create_app()

    # --- New module blueprints -------------------------------------------
    application.register_blueprint(audit_bp)
    application.register_blueprint(reports_bp)

    # --- Serve the existing frontend from the project root ----------------
    application.template_folder = TEMPLATE_DIR
    application.jinja_loader = FileSystemLoader(TEMPLATE_DIR)
    application.static_folder = STATIC_DIR

    @application.route("/")
    def index():
        return render_template("auth/login.html")

    @application.route("/<path:page>")
    def serve_page(page):
        """
        Render any existing template by its path, which reproduces every route
        defined in app.py (/admin/audit/list.html, /reports/exam_report.html,
        and so on) without duplicating them here.
        """
        if not page.endswith(".html"):
            abort(404)

        candidate = os.path.normpath(os.path.join(TEMPLATE_DIR, page))

        if not candidate.startswith(TEMPLATE_DIR) or not os.path.isfile(candidate):
            abort(404)

        return render_template(page)

    return application


app = build_app()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Online Examination Platform - Application Server")
    print("=" * 60)
    print("Frontend      : http://127.0.0.1:5000")
    print("Audit API     : http://127.0.0.1:5000/api/v1/audit/logs")
    print("Reports API   : http://127.0.0.1:5000/api/v1/reports/overview")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
