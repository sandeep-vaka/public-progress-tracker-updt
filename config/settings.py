<<<<<<< HEAD
=======
"""
config/settings.py
──────────────────
Central config class.  All values are loaded from the .env file via
python-dotenv so this file itself never contains secrets.

Phase 1 additions
─────────────────
• BASE_URL         — used to build the verify-email link in emails
• MAIL_*           — Flask-Mail SMTP settings

Phase 4 additions
─────────────────
• UPLOAD_FOLDER        — directory where uploaded files are stored on disk.
                         Defaults to "uploads/" (relative to the app root).
                         Set an absolute path in production if desired.
• MAX_CONTENT_LENGTH   — hard cap on request body size (bytes).
                         Flask rejects any request exceeding this limit with
                         a 413 Request Entity Too Large before the view runs.
                         Default: 10 MB.
"""

>>>>>>> 1aec990 (Your descriptive commit message)
import os
from dotenv import load_dotenv

load_dotenv()

<<<<<<< HEAD
class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/progress_tracker")
    JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
=======

class Config:
    # ── Database ───────────────────────────────────────────────────────────────
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/progress_tracker")

    # ── JWT Auth ───────────────────────────────────────────────────────────────
    JWT_SECRET = os.getenv("JWT_SECRET", "changeme")

    # ── App ────────────────────────────────────────────────────────────────────
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # Public-facing base URL — used when building links inside emails.
    # For local dev this defaults to localhost:5000.
    # In production set this to your actual domain, e.g. https://myapp.com
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

    # ── Flask-Mail (Phase 1) ───────────────────────────────────────────────────
    MAIL_SERVER         = os.getenv("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT           = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS        = os.getenv("MAIL_USE_TLS",  "True")  == "True"
    MAIL_USE_SSL        = os.getenv("MAIL_USE_SSL",  "False") == "False"
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        os.getenv("MAIL_USERNAME", "noreply@progresstracker.com"),
    )

    # ── File Uploads (Phase 4) ─────────────────────────────────────────────────
    # Where uploaded files land on disk (relative to the project root).
    # Override with an absolute path in production, e.g. /var/data/uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")

    # Flask enforces this limit before the view function runs.
    # Value is in bytes: 10 * 1024 * 1024 = 10 MB.
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
>>>>>>> 1aec990 (Your descriptive commit message)
