<<<<<<< HEAD
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class User(Document):
    name = StringField(required=True, max_length=100)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
=======
"""
models/user.py
──────────────
User MongoEngine document.

Phase 1 change
──────────────
Added  is_verified (BooleanField, default=False).
New users start unverified and must click the link in their signup
email before they can log in.  Exposed in to_dict() so the frontend
can display a "pending verification" state if needed.
"""

from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime, timezone


class User(Document):
    name       = StringField(required=True, max_length=100)
    email      = StringField(required=True, unique=True)
    password   = StringField(required=True)

    # Phase 1 — set to True only after the user clicks the email verify link
    is_verified = BooleanField(default=False)

>>>>>>> 1aec990 (Your descriptive commit message)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {"collection": "users"}

    def to_dict(self):
        return {
<<<<<<< HEAD
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
=======
            "id":          str(self.id),
            "name":        self.name,
            "email":       self.email,
            "is_verified": self.is_verified,   # Phase 1: included in responses
            "created_at":  self.created_at.isoformat(),
>>>>>>> 1aec990 (Your descriptive commit message)
        }
