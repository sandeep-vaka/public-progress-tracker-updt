"""
utils/email_utils.py
─────────────────────
Helpers for email-related operations in Phase 1:
  • generate_verification_token  – create a URL-safe, time-limited token
  • confirm_verification_token   – validate the token and return the email
  • send_verification_email      – compose and dispatch the HTML email

Token strategy
--------------
We use itsdangerous.URLSafeTimedSerializer with a dedicated salt so that
the same JWT_SECRET can also be used for password-reset tokens (Phase 2)
without any cross-use risk.  The token embeds the user's email address
and is valid for EMAIL_VERIFICATION_MAX_AGE seconds (default 24 h).
"""

import logging
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from extensions import mail
from config.settings import Config

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
EMAIL_VERIFICATION_SALT = "email-verification-salt"
EMAIL_VERIFICATION_MAX_AGE = 86_400  # 24 hours in seconds


# ── Token helpers ──────────────────────────────────────────────────────────────

def generate_verification_token(email: str) -> str:
    """
    Return a URL-safe signed token that encodes the given email address.
    The token is signed with JWT_SECRET + EMAIL_VERIFICATION_SALT so it
    cannot be forged and is independent of other token types.
    """
    s = URLSafeTimedSerializer(Config.JWT_SECRET)
    return s.dumps(email, salt=EMAIL_VERIFICATION_SALT)


def confirm_verification_token(token: str):
    """
    Validate *token* and return the email it encodes, or None on failure.

    Failure cases:
      - Token was tampered with   → BadSignature  → returns None
      - Token is older than 24 h  → SignatureExpired → returns None
    """
    s = URLSafeTimedSerializer(Config.JWT_SECRET)
    try:
        email = s.loads(
            token,
            salt=EMAIL_VERIFICATION_SALT,
            max_age=EMAIL_VERIFICATION_MAX_AGE,
        )
    except SignatureExpired:
        logger.warning("Email verification token has expired.")
        return None
    except BadSignature:
        logger.warning("Email verification token has an invalid signature.")
        return None
    return email


# ── Email sender ───────────────────────────────────────────────────────────────

def send_verification_email(user_email: str, user_name: str, token: str, base_url: str) -> bool:
    """
    Compose and send an HTML + plain-text verification email.

    Returns True on success, False if Flask-Mail raises any exception
    (e.g. SMTP credentials not configured).  The controller logs a
    debug-mode hint so developers can manually hit the verify URL.
    """
    verify_url = f"{base_url}/api/auth/verify-email/{token}"

    # ── Plain-text fallback ────────────────────────────────────────────────────
    text_body = (
        f"Hi {user_name},\n\n"
        "Welcome to Progress Tracker!\n\n"
        "Please verify your email by visiting:\n"
        f"{verify_url}\n\n"
        "This link expires in 24 hours.\n\n"
        "If you did not create this account, you can safely ignore this email.\n\n"
        "— The Progress Tracker Team"
    )

    # ── HTML body — matches app's purple (#6c63ff) design token ───────────────
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body  {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6;
             color: #111827; margin: 0; padding: 32px 16px; }}
    .wrap {{ max-width: 560px; margin: 0 auto; }}
    .card {{ background: #fff; border-radius: 10px;
             box-shadow: 0 2px 12px rgba(0,0,0,.08); overflow: hidden; }}
    .header {{ background: #6c63ff; padding: 28px 32px; text-align: center; }}
    .header h1 {{ color: #fff; font-size: 22px; margin: 0; letter-spacing: .5px; }}
    .body   {{ padding: 32px; }}
    .body p  {{ line-height: 1.65; margin: 0 0 16px; font-size: 15px; }}
    .btn-wrap {{ text-align: center; margin: 28px 0; }}
    .btn  {{ display: inline-block; background: #6c63ff; color: #fff !important;
             text-decoration: none; padding: 14px 36px; border-radius: 8px;
             font-weight: 700; font-size: 15px; }}
    .url-box {{ background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px;
                padding: 12px 16px; word-break: break-all;
                font-size: 13px; color: #6c63ff; margin-bottom: 20px; }}
    .warn {{ color: #b45309; font-size: 13px; background: #fef3c7;
             border: 1px solid #fde68a; border-radius: 6px;
             padding: 10px 14px; margin-top: 4px; }}
    .footer {{ background: #f3f4f6; border-top: 1px solid #e5e7eb;
               text-align: center; padding: 16px; font-size: 12px; color: #6b7280; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="header"><h1>⚡ ProgressTracker</h1></div>
      <div class="body">
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>
          Thanks for signing up! Please verify your email address to activate
          your account and start tracking your progress.
        </p>
        <div class="btn-wrap">
          <a href="{verify_url}" class="btn">Verify My Email</a>
        </div>
        <p style="font-size:13px; color:#6b7280; margin-bottom:8px;">
          Or copy and paste this link into your browser:
        </p>
        <div class="url-box">{verify_url}</div>
        <p class="warn">
          ⚠️ This link expires in <strong>24 hours</strong>.
          If you did not create this account, you can safely ignore this email.
        </p>
      </div>
      <div class="footer">
        © 2025 Progress Tracker &nbsp;·&nbsp; This is an automated message, please do not reply.
      </div>
    </div>
  </div>
</body>
</html>"""

    try:
        msg = Message(
            subject="Verify Your Progress Tracker Account",
            recipients=[user_email],
            body=text_body,
            html=html_body,
        )
        mail.send(msg)
        logger.info(f"Verification email sent to {user_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send verification email to {user_email}: {exc}")
        return False


# ── Password Reset (Phase 2) ───────────────────────────────────────────────────

PASSWORD_RESET_SALT = "password-reset-salt"
PASSWORD_RESET_MAX_AGE = 1_800  # 30 minutes in seconds


def generate_password_reset_token(email: str) -> str:
    """
    Return a URL-safe signed token encoding the given email address.
    Uses a dedicated salt so reset tokens cannot be replayed as
    verification tokens (and vice-versa), even though both share
    the same JWT_SECRET.
    """
    s = URLSafeTimedSerializer(Config.JWT_SECRET)
    return s.dumps(email, salt=PASSWORD_RESET_SALT)


def confirm_password_reset_token(token: str):
    """
    Validate *token* and return the email it encodes, or None on failure.

    Failure cases:
      - Token was tampered with   → BadSignature      → returns None
      - Token is older than 30 min → SignatureExpired → returns None
    """
    s = URLSafeTimedSerializer(Config.JWT_SECRET)
    try:
        email = s.loads(
            token,
            salt=PASSWORD_RESET_SALT,
            max_age=PASSWORD_RESET_MAX_AGE,
        )
    except SignatureExpired:
        logger.warning("Password reset token has expired.")
        return None
    except BadSignature:
        logger.warning("Password reset token has an invalid signature.")
        return None
    return email


def send_password_reset_email(user_email: str, user_name: str, token: str, base_url: str) -> bool:
    """
    Compose and dispatch an HTML + plain-text password-reset email.

    Returns True on success, False if Flask-Mail raises any exception.
    The reset link is valid for 30 minutes.
    """
    reset_url = f"{base_url}/api/auth/reset-password/{token}"

    text_body = (
        f"Hi {user_name},\n\n"
        "We received a request to reset your Progress Tracker password.\n\n"
        "Reset your password by visiting:\n"
        f"{reset_url}\n\n"
        "This link expires in 30 minutes.\n\n"
        "If you did not request a password reset, you can safely ignore this email — "
        "your password will not change.\n\n"
        "— The Progress Tracker Team"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body  {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6;
             color: #111827; margin: 0; padding: 32px 16px; }}
    .wrap {{ max-width: 560px; margin: 0 auto; }}
    .card {{ background: #fff; border-radius: 10px;
             box-shadow: 0 2px 12px rgba(0,0,0,.08); overflow: hidden; }}
    .header {{ background: #6c63ff; padding: 28px 32px; text-align: center; }}
    .header h1 {{ color: #fff; font-size: 22px; margin: 0; letter-spacing: .5px; }}
    .body   {{ padding: 32px; }}
    .body p  {{ line-height: 1.65; margin: 0 0 16px; font-size: 15px; }}
    .btn-wrap {{ text-align: center; margin: 28px 0; }}
    .btn  {{ display: inline-block; background: #6c63ff; color: #fff !important;
             text-decoration: none; padding: 14px 36px; border-radius: 8px;
             font-weight: 700; font-size: 15px; }}
    .url-box {{ background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px;
                padding: 12px 16px; word-break: break-all;
                font-size: 13px; color: #6c63ff; margin-bottom: 20px; }}
    .warn {{ color: #b45309; font-size: 13px; background: #fef3c7;
             border: 1px solid #fde68a; border-radius: 6px;
             padding: 10px 14px; margin-top: 4px; }}
    .footer {{ background: #f3f4f6; border-top: 1px solid #e5e7eb;
               text-align: center; padding: 16px; font-size: 12px; color: #6b7280; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="header"><h1>⚡ ProgressTracker</h1></div>
      <div class="body">
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>
          We received a request to reset the password for your account.
          Click the button below to choose a new password.
        </p>
        <div class="btn-wrap">
          <a href="{reset_url}" class="btn">Reset My Password</a>
        </div>
        <p style="font-size:13px; color:#6b7280; margin-bottom:8px;">
          Or copy and paste this link into your browser:
        </p>
        <div class="url-box">{reset_url}</div>
        <p class="warn">
          ⏱️ This link expires in <strong>30 minutes</strong>.
          If you did not request a password reset, you can safely ignore this
          email — your password will not change.
        </p>
      </div>
      <div class="footer">
        © 2025 Progress Tracker &nbsp;·&nbsp; This is an automated message, please do not reply.
      </div>
    </div>
  </div>
</body>
</html>"""

    try:
        msg = Message(
            subject="Reset Your Progress Tracker Password",
            recipients=[user_email],
            body=text_body,
            html=html_body,
        )
        mail.send(msg)
        logger.info(f"Password reset email sent to {user_email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send password reset email to {user_email}: {exc}")
        return False
