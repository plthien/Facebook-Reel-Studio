"""Redacted local evidence writer and resumable nonsecret operation journal."""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

KEY_RE = re.compile(r"(?i)(token|secret|authorization|password|signed|signature|api_key|code|upload_url)")
INLINE_SECRET_RE = re.compile(r"(?i)(access_token|client_secret|authorization|code|appsecret_proof)=([^&\s]+)")


def redact(value: Any) -> Any:
    """Defense-in-depth allow-list friendly sanitizer; filter unknown nested secrets."""
    if isinstance(value, dict):
        return {str(k): ("[REDACTED]" if KEY_RE.search(str(k)) else redact(v))
                for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(x) for x in value]
    if isinstance(value, str):
        clean = INLINE_SECRET_RE.sub(lambda m: m.group(1) + "=[REDACTED]", value)
        if clean.startswith("https://"):
            p = urlsplit(clean)
            if p.hostname in {"rupload.facebook.com", "graph.facebook.com"}:
                return urlunsplit((p.scheme, p.netloc, p.path, "", ""))
        return clean
    return value


def secure_write(path: Path, payload: dict[str, Any]) -> None:
    """Atomic replace; evidence stores safe metadata only, never credentials."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("Evidence path must not be symbolic link")
    fd, filename = tempfile.mkstemp(dir=path.parent, prefix=".p0tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            os.chmod(filename, 0o600)
            json.dump(redact(payload), handle, indent=2, sort_keys=True)
        os.replace(filename, path)
        os.chmod(path, 0o600)
    finally:
        Path(filename).unlink(missing_ok=True)


def journal_event(directory: Path, *, phase: str, page_id: str | None = None,
                  video_id: str | None = None, state: str = "UNCERTAIN",
                  extra: dict[str, Any] | None = None) -> Path:
    """Store recovery identifiers under the explicitly local gitignored directory."""
    event = {"observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "phase": phase, "page_id": page_id, "video_id": video_id, "state": state,
             "details": redact(extra or {})}
    existing = directory / "journal.json"
    data: dict[str, Any] = {"schema_version": 1, "events": []}
    if existing.is_file():
        try:
            with existing.open("r", encoding="utf-8") as handle:
                read = json.load(handle)
            if isinstance(read, dict) and isinstance(read.get("events"), list):
                data = read
        except (OSError, ValueError):
            raise ValueError("Existing journal unreadable; cannot replace safely") from None
    data["events"].append(event)
    secure_write(existing, data)
    return existing


def export_evidence(directory: Path) -> dict[str, Any]:
    """Only safe journal data, no raw Graph responses or secrets, for reviewer inspection."""
    path = directory / "journal.json"
    if not path.exists():
        return {"events": [], "source": "NO_LOCAL_EVENTS"}
    with path.open("r", encoding="utf-8") as handle:
        journal = json.load(handle)
    if not isinstance(journal, dict):
        raise ValueError("Malformed journal")
    return redact(journal)

