"""One-time short-lived OAuth state; callback URL is never printed."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from urllib.parse import parse_qs, urlencode, urlsplit

from app.config import Settings


def create_auth_url(settings: Settings, *, now: float | None = None) -> str:
    if settings.missing("app_id", "redirect_uri"):
        raise ValueError("META_APP_ID and META_REDIRECT_URI required")
    state = secrets.token_urlsafe(32)
    data = {"hash": hashlib.sha256(state.encode()).hexdigest(),
            "expires_at": (now if now is not None else time.time()) + 600}
    path = settings.state_file
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    query = urlencode({"client_id": settings.app_id, "redirect_uri": settings.redirect_uri,
                       "state": state, "response_type": "code",
                       "scope": "pages_show_list,pages_read_engagement,pages_manage_posts,read_insights"})
    return "https://www.facebook.com/" + settings.graph_version + "/dialog/oauth?" + query


def consume_callback(settings: Settings, callback_url: str, *, now: float | None = None) -> str:
    parsed, expected = urlsplit(callback_url), urlsplit(settings.redirect_uri)
    if (parsed.scheme, parsed.netloc, parsed.path) != (expected.scheme, expected.netloc, expected.path):
        raise ValueError("Callback origin/path mismatch")
    q = parse_qs(parsed.query)
    state, code = q.get("state", []), q.get("code", [])
    if len(state) != 1 or len(code) != 1:
        raise ValueError("Missing or ambiguous callback state/code")
    path = settings.state_file
    try:
        with path.open("r", encoding="utf-8") as handle:
            saved = json.load(handle)
    except (OSError, ValueError):
        raise ValueError("No outstanding OAuth session") from None
    finally:
        path.unlink(missing_ok=True)
    digest = hashlib.sha256(state[0].encode()).hexdigest()
    if not secrets.compare_digest(digest, str(saved.get("hash", ""))) or (
        now if now is not None else time.time()) >= saved.get("expires_at", 0):
        raise ValueError("OAuth state invalid, expired or replayed")
    return code[0]
