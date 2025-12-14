"""
Authentication module (Group F)

Provides a simple username/password authentication system.
"""

from __future__ import annotations
from typing import Dict, Any


class AuthSystem:
    """Simple authentication system holding a username->password map.

    This class provides serialization helpers so the user database can
    be persisted and restored by `storage.py`.
    """

    def __init__(self, users: Dict[str, str] | None = None) -> None:
        self.users: Dict[str, str] = dict(users or {})

    def authenticate(self, username: str, password: str) -> bool:
        return self.users.get(username) == password

    def register_user(self, username: str, password: str) -> bool:
        if username in self.users:
            return False
        self.users[username] = password
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"users": dict(self.users)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthSystem":
        users = (data.get("users") or {})
        return cls(users=users)


# Backwards-compatible helper functions that operate on plain dicts
def authenticate(username: str, password: str, user_db: Dict[str, str]) -> bool:
    return user_db.get(username) == password


def register_user(username: str, password: str, user_db: Dict[str, str]) -> bool:
    if username in user_db:
        return False
    user_db[username] = password
    return True