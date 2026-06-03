
"""
models/progress.py
──────────────────
Progress document model.

Phase 4 additions
─────────────────
• file_url  — relative path where the uploaded file is stored on disk,
              e.g. "uploads/abc123_report.pdf".  None when no file attached.
• file_name — original sanitised filename as shown to the user,
              e.g. "report.pdf".  None when no file attached.

Both fields are optional (default None) so existing documents that pre-date
Phase 4 continue to work without any migration.
"""

from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

PROGRESS_STATUS = ("not_started", "in_progress", "completed")

class Progress(Document):
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    progress_status = StringField(required=True, choices=PROGRESS_STATUS, default="not_started")
    created_by = ReferenceField(User, required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


class Progress(Document):
    title           = StringField(required=True, max_length=200)
    description     = StringField(max_length=1000)
    progress_status = StringField(required=True, choices=PROGRESS_STATUS, default="not_started")
    created_by      = ReferenceField(User, required=True)
    created_at      = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at      = DateTimeField(default=lambda: datetime.now(timezone.utc))

    # ── Phase 4: file attachment ──────────────────────────────────────────────
    # file_url  stores the path relative to the app root, e.g. "uploads/abc.pdf"
    # file_name stores the human-readable original name shown in API responses
    file_url  = StringField(default=None)
    file_name = StringField(default=None)


    meta = {"collection": "progress"}

    def to_dict(self):
        return {

            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "progress_status": self.progress_status,
            "created_by": self.created_by.to_dict() if self.created_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),

            "id":              str(self.id),
            "title":           self.title,
            "description":     self.description,
            "progress_status": self.progress_status,
            "created_by":      self.created_by.to_dict() if self.created_by else None,
            "created_at":      self.created_at.isoformat(),
            "updated_at":      self.updated_at.isoformat(),
            # Phase 4 — always present; null when no file is attached
            "file_url":        self.file_url,
            "file_name":       self.file_name,

        }
