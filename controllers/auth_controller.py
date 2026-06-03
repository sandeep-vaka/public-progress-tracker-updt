
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from config.settings import Config
import jwt
from datetime import datetime, timedelta, timezone


def signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()

"""
controllers/auth_controller.py
───────────────────────────────
Auth logic: signup, login, email verification, and (Phase 2) password reset.

Phase 2 additions
─────────────────
forgot_password()
  • POST /api/auth/forgot-password
  • Accepts {"email": "user@example.com"}.
  • Always returns HTTP 200 with a generic message so that the endpoint
    cannot be used to enumerate registered email addresses.
  • If the email exists and is verified, generates a 30-minute
    itsdangerous reset token and dispatches a password-reset email.
  • In DEBUG mode the raw reset URL is printed to the console for
    local testing without a live mail server.

reset_password(token)
  • POST /api/auth/reset-password/<token>
  • Accepts {"password": "NewPassword123"}.
  • Validates the token (30-minute window, tamper-proof).
  • Enforces the same password strength rules as signup.
  • Re-hashes the new password using Werkzeug (identical to signup path).
  • Returns JSON — this endpoint is called from a form/fetch, not a
    browser link click, so HTML rendering is not needed.
"""

import logging
import re
from datetime import datetime, timedelta, timezone

import jwt
from flask import jsonify, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

from config.settings import Config
from models.user import User
from utils.email_utils import (
    confirm_verification_token,
    generate_verification_token,
    send_verification_email,
    confirm_password_reset_token,
    generate_password_reset_token,
    send_password_reset_email,
)

logger = logging.getLogger(__name__)

# ── Password validation ────────────────────────────────────────────────────────

_PASSWORD_MIN_LEN = 8
_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$"
)


def _validate_password(password: str):
    """
    Return an error string if *password* fails requirements, else None.

    Rules (match existing signup constraints implied by the spec):
      • At least 8 characters
      • At least one uppercase letter
      • At least one lowercase letter
      • At least one digit
    """
    if len(password) < _PASSWORD_MIN_LEN:
        return f"Password must be at least {_PASSWORD_MIN_LEN} characters long."
    if not _PASSWORD_RE.match(password):
        return (
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, and one digit."
        )
    return None


# ── Signup ────────────────────────────────────────────────────────────────────

def signup():
    data     = request.get_json()
    name     = data.get("name",     "").strip()
    email    = data.get("email",    "").strip().lower()
>>>>>>> 1aec990 (Your descriptive commit message)
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.objects(email=email).first():
        return jsonify({"error": "Email already registered"}), 409


    hashed = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed).save()

    return jsonify({"message": "User created", "user": user.to_dict()}), 201


def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    # Hash password and persist the user (is_verified defaults to False)
    hashed = generate_password_hash(password)
    user   = User(name=name, email=email, password=hashed).save()

    # Generate token and attempt to send the verification email
    token      = generate_verification_token(email)
    email_sent = send_verification_email(email, name, token, Config.BASE_URL)

    if email_sent:
        message = "Account created. Please check your email to verify your account."
    else:
        # Email failed — give the developer the raw URL so they can verify manually
        logger.warning(f"Verification email could not be sent to {email}.")
        if Config.DEBUG:
            verify_url = f"{Config.BASE_URL}/api/auth/verify-email/{token}"
            logger.info(f"[DEV] Manual verify URL → {verify_url}")
        message = (
            "Account created, but we could not send a verification email. "
            "Please contact support."
        )

    return jsonify({"message": message, "user": user.to_dict()}), 201


# ── Login ─────────────────────────────────────────────────────────────────────

def login():
    data     = request.get_json()
    email    = data.get("email",    "").strip().lower()

    password = data.get("password", "")

    user = User.objects(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401


    payload = {
        "user_id": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),

    # Phase 1 — block unverified accounts before issuing any token
    if not user.is_verified:
        return jsonify({"message": "Please verify your email before logging in."}), 403

    payload = {
        "user_id": str(user.id),
        "exp":     datetime.now(timezone.utc) + timedelta(days=7),

    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "user": user.to_dict()}), 200



# ── Email verification ────────────────────────────────────────────────────────

def verify_email(token):
    """
    GET /api/auth/verify-email/<token>

    This endpoint is reached by clicking the link in the signup email, so
    we render an HTML page rather than returning plain JSON — users arrive
    here in a browser tab, not from fetch().
    """
    email = confirm_verification_token(token)

    if email is None:
        # Token is tampered-with or older than 24 hours
        return render_template(
            "email_verified.html",
            success=False,
            message=(
                "The verification link is invalid or has expired (links are valid for 24 hours). "
                "Please sign up again or contact support."
            ),
        ), 400

    user = User.objects(email=email).first()
    if not user:
        return render_template(
            "email_verified.html",
            success=False,
            message="No account found for this email address.",
        ), 404

    if user.is_verified:
        # Idempotent — clicking the link twice is not an error
        return render_template(
            "email_verified.html",
            success=True,
            message="Your email address is already verified. You can log in.",
        ), 200

    # Mark the user as verified and persist the change
    user.is_verified = True
    user.updated_at  = datetime.now(timezone.utc)
    user.save()

    logger.info(f"User {email} successfully verified their email.")

    return render_template(
        "email_verified.html",
        success=True,
        message="Your email has been verified successfully! You can now log in.",
    ), 200


# ── Forgot password (Phase 2) ─────────────────────────────────────────────────

def forgot_password():
    """
    POST /api/auth/forgot-password
    Body: {"email": "user@example.com"}

    Always responds with HTTP 200 and a generic message to prevent email
    enumeration attacks — the caller cannot tell whether an address is
    registered or not from the response alone.

    If the email belongs to a verified account a 30-minute reset token is
    generated and dispatched.  Unverified accounts are silently skipped
    (they should complete email verification first).
    """
    data  = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    # Validate input format before doing any DB work
    if not email:
        return jsonify({"error": "email is required"}), 400

    # Generic response — do not leak whether the address exists
    generic_message = (
        "If that email address is registered and verified, "
        "you will receive a password-reset link shortly."
    )

    user = User.objects(email=email).first()

    # Silently do nothing for unknown or unverified addresses
    if not user or not user.is_verified:
        logger.info(
            f"Forgot-password request for {'unverified' if user else 'unknown'} "
            f"address: {email}"
        )
        return jsonify({"message": generic_message}), 200

    token      = generate_password_reset_token(email)
    email_sent = send_password_reset_email(email, user.name, token, Config.BASE_URL)

    if not email_sent:
        logger.warning(f"Password reset email could not be sent to {email}.")
        if Config.DEBUG:
            reset_url = f"{Config.BASE_URL}/api/auth/reset-password/{token}"
            logger.info(f"[DEV] Manual reset URL → {reset_url}")

    return jsonify({"message": generic_message}), 200


# ── Reset password (Phase 2) ──────────────────────────────────────────────────

def reset_password(token):
    """
    POST /api/auth/reset-password/<token>
    Body: {"password": "NewPassword123"}

    Validates the itsdangerous token (30-minute window), applies password
    strength rules, then re-hashes and persists the new password using the
    same Werkzeug helper as signup — no deviation from the existing hashing
    logic.
    """
    # 1. Validate the token first — before touching the request body
    email = confirm_password_reset_token(token)
    if email is None:
        return jsonify({
            "error": "The reset link is invalid or has expired. Please request a new one."
        }), 400

    # 2. Parse and validate the new password
    data     = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "password is required"}), 400

    error = _validate_password(password)
    if error:
        return jsonify({"error": error}), 400

    # 3. Look up the account
    user = User.objects(email=email).first()
    if not user:
        # Should not normally happen (token encodes a real email), but be safe
        return jsonify({"error": "No account found for this reset link."}), 404

    # 4. Hash and persist — identical path to signup
    user.password   = generate_password_hash(password)
    user.updated_at = datetime.now(timezone.utc)
    user.save()

    logger.info(f"Password successfully reset for {email}.")

    return jsonify({"message": "Your password has been reset successfully. You can now log in."}), 200

