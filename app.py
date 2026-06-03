
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from config.db import init_db
from config.settings import Config
from routes.auth_routes import auth_bp
from routes.progress_routes import progress_bp
import os

"""
app.py
──────
Flask application factory.

Phase 1 change
──────────────
• Imports the shared `mail` singleton from extensions.py and wires it
  to the app with mail.init_app(app) — this is the standard Flask
  extension pattern that avoids circular imports.

Phase 4 change
──────────────
• Ensures the UPLOAD_FOLDER directory exists at startup so the first
  upload never fails with a "directory not found" error.
• Registers a 413 error handler so oversized uploads get a clean JSON
  response instead of an HTML error page.
"""

import os

from flask import Flask, jsonify, render_template
from flask_cors import CORS

from config.db import init_db
from config.settings import Config
from extensions import mail
from routes.auth_routes import auth_bp
from routes.progress_routes import progress_bp


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(Config)


    CORS(app)
    init_db()

    # API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(progress_bp)

    # ── Frontend routes ──────────────────────────────────────

    # ── Phase 4: ensure upload directory exists ───────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────────
    CORS(app)
    mail.init_app(app)
    init_db()

    # ── API blueprints ────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(progress_bp)

    # ── Frontend routes ───────────────────────────────────────────────────────

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/signup")
    def signup_page():
        return render_template("signup.html")

    @app.get("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    @app.get("/public")
    def public_page():
        return render_template("public.html")

    # ── Error handlers ───────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        # API 404
        if "/api/" in str(e):
            return jsonify({"error": "Route not found"}), 404
        return render_template("index.html"), 404   # SPA fallback

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if "/api/" in str(e):
            return jsonify({"error": "Route not found"}), 404
        return render_template("index.html"), 404


    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    # Phase 4: clean JSON response when an upload exceeds MAX_CONTENT_LENGTH
    @app.errorhandler(413)
    def request_too_large(e):
        max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        return jsonify({"error": f"File too large. Maximum size is {max_mb} MB."}), 413


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, port=5000)
