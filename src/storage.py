"""
storage.py

(Expanded) Persistence layer: save/load the full system state (library + auth) to JSON.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Tuple

from library import Library
from auth_system import AuthSystem


def load_state(path: str | Path) -> Tuple[Library, AuthSystem]:
    p = Path(path)
    if not p.exists():
        return Library(), AuthSystem()
    data = json.loads(p.read_text(encoding="utf-8"))
    library = Library.from_dict(data.get("library", {}) or {})
    auth = AuthSystem.from_dict(data.get("auth", {}) or {})
    return library, auth


def save_state(path: str | Path, library: Library, auth: AuthSystem) -> None:
    p = Path(path)
    data: Dict[str, Any] = {"library": library.to_dict(), "auth": auth.to_dict()}
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")