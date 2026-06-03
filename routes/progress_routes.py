
"""
routes/progress_routes.py
──────────────────────────
Progress Blueprint route registration.

Phase 4 additions
─────────────────
• GET /api/progress/uploads/<filename>  — serve a stored attachment
  (protected: requires a valid JWT so random visitors cannot download files)
"""


from flask import Blueprint
from middleware.auth_middleware import token_required
from controllers.progress_controller import (
    create_progress,
    get_my_progress,
    update_progress,
    delete_progress,
    get_all_progress,

    serve_file,           # Phase 4

)

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")


# Public
progress_bp.get("/public")(get_all_progress)

# Protected

# ── Public ─────────────────────────────────────────────────────────────────────
progress_bp.get("/public")(get_all_progress)

# ── Protected ──────────────────────────────────────────────────────────────────

progress_bp.post("/")(token_required(create_progress))
progress_bp.get("/")(token_required(get_my_progress))
progress_bp.put("/<progress_id>")(token_required(update_progress))
progress_bp.delete("/<progress_id>")(token_required(delete_progress))



# Phase 4: file serving — authenticated so only logged-in users can download
progress_bp.get("/uploads/<path:filename>")(token_required(lambda u, **kw: serve_file(**kw)))

