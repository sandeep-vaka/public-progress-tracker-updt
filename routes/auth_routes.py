
from flask import Blueprint
from controllers.auth_controller import signup, login

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_bp.post("/signup")(signup)
auth_bp.post("/login")(login)

"""
routes/auth_routes.py
─────────────────────
Blueprint for all /api/auth/* endpoints.

Phase 1 addition
────────────────
GET /api/auth/verify-email/<token>
  Validates the signed email-verification token and marks the account
  as verified.  Renders an HTML result page since users arrive via a
  browser link in their signup email.

Phase 2 additions
─────────────────
POST /api/auth/forgot-password
  Accepts {"email": "user@example.com"}.  Generates a 30-minute reset
  token and dispatches a password-reset email.  Always returns 200 with
  a generic message to prevent email enumeration.

POST /api/auth/reset-password/<token>
  Accepts {"password": "NewPassword123"}.  Validates the token and
  replaces the stored password hash using the same Werkzeug path as
  signup.
"""

from flask import Blueprint
from controllers.auth_controller import (
    login,
    signup,
    verify_email,
    forgot_password,
    reset_password,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ── Existing endpoints (unchanged) ────────────────────────────────────────────
auth_bp.post("/signup")(signup)
auth_bp.post("/login")(login)

# ── Phase 1: Email verification ───────────────────────────────────────────────
auth_bp.get("/verify-email/<token>")(verify_email)

# ── Phase 2: Password reset ───────────────────────────────────────────────────
auth_bp.post("/forgot-password")(forgot_password)
auth_bp.post("/reset-password/<token>")(reset_password)

