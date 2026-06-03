"""
utils/file_utils.py
────────────────────
File-upload helpers for Phase 4.

Responsibilities
────────────────
1. ALLOWED_EXTENSIONS  — the set of permitted file extensions.
2. allowed_file()      — validates that an uploaded filename has a permitted
                         extension.
3. save_upload()       — sanitises the filename, generates a unique prefix to
                         prevent collisions, persists the file to UPLOAD_FOLDER,
                         and returns (file_url, file_name) ready to store in
                         MongoDB.
4. delete_upload()     — removes a previously stored file from disk; silently
                         ignores missing files so callers need no try/except.

Design notes
────────────
• werkzeug's secure_filename() strips path traversal characters and other
  unsafe sequences.  We prepend a uuid4 hex so two uploads of "report.pdf"
  never collide.
• file_url is stored as a *relative* path ("uploads/<uuid>_<name>") so the
  app remains portable across machines / deployment environments.
• The upload directory is created automatically on first use.
"""

import os
import uuid

from werkzeug.utils import secure_filename

# ── Permitted file types ───────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "docx"}


def allowed_file(filename: str) -> bool:
    """
    Return True iff *filename* has a dot and an allowed extension.

    Examples
    ────────
    >>> allowed_file("photo.jpg")   # True
    >>> allowed_file("script.exe")  # False
    >>> allowed_file("noextension") # False
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_upload(file, upload_folder: str) -> tuple[str, str]:
    """
    Persist *file* (a werkzeug FileStorage object) to *upload_folder*.

    Steps
    ─────
    1. Sanitise the original filename with secure_filename().
    2. Prepend a uuid4 hex segment to guarantee uniqueness.
    3. Create *upload_folder* if it does not already exist.
    4. Write the file to disk.

    Returns
    ───────
    (file_url, file_name) where:
      • file_url  — path relative to the app root, e.g. "uploads/abc_report.pdf"
      • file_name — clean original filename shown to users, e.g. "report.pdf"
    """
    safe_name   = secure_filename(file.filename)          # strip bad chars
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"       # collision-proof
    file_url    = os.path.join(upload_folder, unique_name)

    os.makedirs(upload_folder, exist_ok=True)
    file.save(file_url)

    return file_url, safe_name


def delete_upload(file_url: str | None) -> None:
    """
    Remove the file at *file_url* from disk.

    Silently returns if *file_url* is None or the file does not exist,
    so callers can unconditionally call this without extra guards.
    """
    if file_url and os.path.exists(file_url):
        os.remove(file_url)
