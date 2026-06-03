
from flask import request, jsonify
from datetime import datetime, timezone
from models.progress import Progress


def create_progress(current_user):
    data = request.get_json()

"""
controllers/progress_controller.py
────────────────────────────────────
Progress CRUD logic.

Phase 3 changes  (get_my_progress + get_all_progress)
──────────────────────────────────────────────────────
Both GET endpoints now accept optional query parameters:

  ?search=<text>          — case-insensitive substring match on title OR description
  ?status=<value>         — exact match on progress_status
                            accepted values: not_started | in_progress | completed
  ?page=<int>             — 1-based page number (default 1)
  ?per_page=<int>         — items per page (default 20, max 100)

Parameters may be combined freely; omitting a parameter means "no filter on
that dimension."

Phase 4 changes  (file uploads)
────────────────────────────────
• create_progress  — now accepts multipart/form-data so a file can be
                     uploaded together with the JSON fields.  Falls back to
                     JSON-only for clients that don't attach a file.
• update_progress  — same multipart support; if a new file is uploaded the
                     previous one is deleted from disk first.
• delete_progress  — now also deletes the associated file from disk when the
                     Progress entry is removed.
• serve_file       — new endpoint; streams the stored file back to the client
                     with Flask's send_from_directory so files are never
                     served by guessing a direct filesystem path from user
                     input.

Implementation notes
────────────────────
• Search uses MongoDB's $regex operator with the re.IGNORECASE flag so that
  queries are evaluated server-side and no full collection scan into Python
  memory is required.
• The two conditions (search, status) are built as separate Q objects and
  ANDed together before being passed to MongoEngine — this keeps the query
  composable and easy to extend in future phases.
• Pagination is applied after filtering via MongoEngine's .skip()/.limit()
  slicing, which translates directly to MongoDB cursor skip/limit.
• The response envelope is unchanged for plain list calls so existing
  clients are unaffected; when pagination params are present, results are
  wrapped in a metadata envelope (see _paginate helper).
• File uploads use multipart/form-data.  Text fields (title, description,
  progress_status) are read from request.form; the file comes from
  request.files["file"].  Clients that omit the file field continue to work
  unchanged.
"""

import os
import re
from datetime import datetime, timezone

from flask import jsonify, request, send_from_directory, current_app
from mongoengine.queryset.visitor import Q

from models.progress import Progress, PROGRESS_STATUS
from utils.file_utils import allowed_file, save_upload, delete_upload


# ── Internal helpers ───────────────────────────────────────────────────────────

def _build_query(extra_filter: Q | None = None) -> Q:
    """
    Parse ?search and ?status from the current request and return a
    combined MongoEngine Q object.  *extra_filter* is ANDed in when
    provided (used by get_my_progress to scope results to the current user).
    """
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip().lower()

    conditions = extra_filter if extra_filter is not None else Q()

    # ── Search: title OR description (case-insensitive regex) ─────────────
    if search:
        pattern = re.escape(search)
        conditions &= Q(title__icontains=pattern) | Q(description__icontains=pattern)

    # ── Status: exact match, validated against allowed values ─────────────
    if status:
        if status not in PROGRESS_STATUS:
            raise ValueError(
                f"Invalid status '{status}'. "
                f"Allowed values: {', '.join(PROGRESS_STATUS)}."
            )
        conditions &= Q(progress_status=status)

    return conditions


def _parse_pagination() -> tuple[int, int]:
    """
    Parse ?page and ?per_page from the current request.
    Returns (page, per_page) with sane defaults and bounds.
    Raises ValueError with a human-readable message on bad input.
    """
    try:
        page     = int(request.args.get("page",     1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        raise ValueError("'page' and 'per_page' must be integers.")

    if page < 1:
        raise ValueError("'page' must be >= 1.")
    if not (1 <= per_page <= 100):
        raise ValueError("'per_page' must be between 1 and 100.")

    return page, per_page


def _paginate(queryset, page: int, per_page: int) -> dict:
    """
    Apply skip/limit to *queryset* and return a pagination envelope:

      {
        "results":   [...],
        "total":     <int>,
        "page":      <int>,
        "per_page":  <int>,
        "pages":     <int>
      }
    """
    total = queryset.count()
    items = queryset.skip((page - 1) * per_page).limit(per_page)
    return {
        "results":  [p.to_dict() for p in items],
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    max(1, -(-total // per_page)),
    }


def _handle_file_upload(progress: Progress) -> None:
    """
    If the current request includes a file under the key "file", validate
    it, delete the previous attachment (if any), then save the new one and
    update *progress* in-place.

    Does nothing when no file is present in the request so existing
    JSON-only calls continue to work unchanged.

    Raises ValueError with a user-facing message on validation failure.
    """
    file = request.files.get("file")
    if not file or file.filename == "":
        return  # no file attached — nothing to do

    if not allowed_file(file.filename):
        raise ValueError(
            "File type not allowed. "
            "Accepted types: JPG, JPEG, PNG, PDF, DOCX."
        )

    # Remove the old file from disk before saving the replacement
    delete_upload(progress.file_url)

    upload_folder       = current_app.config["UPLOAD_FOLDER"]
    file_url, file_name = save_upload(file, upload_folder)

    progress.file_url  = file_url
    progress.file_name = file_name


# ── Endpoints ──────────────────────────────────────────────────────────────────

def create_progress(current_user):
    """
    POST /api/progress/

    Accepts either:
      • application/json          — classic JSON body (no file)
      • multipart/form-data       — form fields + optional file attachment

    Required field : title
    Optional fields: description, progress_status, file (binary)
    """
    # Support both JSON and multipart/form-data
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
    else:
        data = request.get_json() or {}

>>>>>>> 1aec990 (Your descriptive commit message)
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    progress = Progress(

        title=title,
        description=data.get("description", ""),
        progress_status=data.get("progress_status", "not_started"),
        created_by=current_user,
    ).save()


        title           = title,
        description     = data.get("description", ""),
        progress_status = data.get("progress_status", "not_started"),
        created_by      = current_user,
    )

    # ── Phase 4: optional file attachment ─────────────────────────────────
    try:
        _handle_file_upload(progress)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    progress.save()

    return jsonify({"message": "Progress created", "progress": progress.to_dict()}), 201


def get_my_progress(current_user):

    items = Progress.objects(created_by=current_user)
    return jsonify([p.to_dict() for p in items]), 200


def update_progress(current_user, progress_id):

    """
    GET /api/progress/
    Returns the authenticated user's progress items, optionally filtered.

    Query params: search, status, page, per_page
    """
    try:
        query          = _build_query(extra_filter=Q(created_by=current_user))
        page, per_page = _parse_pagination()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    qs = Progress.objects(query).order_by("-created_at")

    if "page" not in request.args and "per_page" not in request.args:
        return jsonify([p.to_dict() for p in qs]), 200

    return jsonify(_paginate(qs, page, per_page)), 200


def update_progress(current_user, progress_id):
    """
    PUT /api/progress/<progress_id>

    Accepts either application/json or multipart/form-data.
    When a new file is uploaded the previous attachment is deleted from disk.
    """
>>>>>>> 1aec990 (Your descriptive commit message)
    progress = Progress.objects(id=progress_id, created_by=current_user).first()
    if not progress:
        return jsonify({"error": "Not found or unauthorized"}), 404


    data = request.get_json()
    progress.title = data.get("title", progress.title)
    progress.description = data.get("description", progress.description)
    progress.progress_status = data.get("progress_status", progress.progress_status)
    progress.updated_at = datetime.now(timezone.utc)
    progress.save()


    # Support both JSON and multipart/form-data
    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form
    else:
        data = request.get_json() or {}

    progress.title           = data.get("title",           progress.title)
    progress.description     = data.get("description",     progress.description)
    progress.progress_status = data.get("progress_status", progress.progress_status)
    progress.updated_at      = datetime.now(timezone.utc)

    # ── Phase 4: replace file if a new one was supplied ───────────────────
    try:
        _handle_file_upload(progress)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    progress.save()

    return jsonify({"message": "Updated", "progress": progress.to_dict()}), 200


def delete_progress(current_user, progress_id):


    """
    DELETE /api/progress/<progress_id>

    Phase 4: also removes the associated file from disk when present.
    """

    progress = Progress.objects(id=progress_id, created_by=current_user).first()
    if not progress:
        return jsonify({"error": "Not found or unauthorized"}), 404



    # Phase 4: clean up the stored file before deleting the document
    delete_upload(progress.file_url)


    progress.delete()
    return jsonify({"message": "Deleted"}), 200



# Public endpoint — no auth
def get_all_progress():
    items = Progress.objects().order_by("-created_at")
    return jsonify([p.to_dict() for p in items]), 200

def get_all_progress():
    """
    GET /api/progress/public
    Public endpoint — returns all progress items, optionally filtered.

    Query params: search, status, page, per_page
    """
    try:
        query          = _build_query()
        page, per_page = _parse_pagination()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    qs = Progress.objects(query).order_by("-created_at")

    if "page" not in request.args and "per_page" not in request.args:
        return jsonify([p.to_dict() for p in qs]), 200

    return jsonify(_paginate(qs, page, per_page)), 200


def serve_file(filename):
    """
    GET /api/progress/uploads/<filename>

    Streams the requested file from UPLOAD_FOLDER using Flask's
    send_from_directory, which prevents directory-traversal attacks by
    refusing to serve paths outside the designated folder.

    Only authenticated users can reach this endpoint (enforced in routes).
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    # Resolve to an absolute path so send_from_directory works regardless of
    # how the app is launched (e.g. from a sub-directory in production).
    abs_folder = os.path.abspath(upload_folder)

    return send_from_directory(abs_folder, filename, as_attachment=False)

