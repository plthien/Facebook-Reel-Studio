"""Strict Meta HTTP boundary: safe read retries, no automatic write replay."""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

import httpx


class MetaFailure(Exception):
    def __init__(self, category: str, phase: str = "READ", code: int | None = None):
        self.category, self.phase, self.code = category, phase, code
        super().__init__(f"{category} phase={phase} code={code}")


class RemoteUncertain(MetaFailure):
    def __init__(self, phase: str, video_id: str | None = None):
        self.video_id = video_id
        super().__init__("UNCERTAIN", phase)


def numeric_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch("[0-9]{1,50}", value):
        raise ValueError("Invalid Meta numeric string ID")
    return value


def validate_upload_url(url: str, video_id: str) -> None:
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname != "rupload.facebook.com" or
            p.username or p.password or p.port is not None or
            p.query or p.fragment or not p.path.startswith("/video-upload/") or
            not p.path.endswith("/" + numeric_id(video_id))):
        raise ValueError("Untrusted upload destination")


def classify(status: int, payload: object, phase: str) -> MetaFailure:
    e = payload.get("error", {}) if isinstance(payload, dict) else {}
    code = e.get("code") if isinstance(e, dict) else None
    code = code if isinstance(code, int) else None
    if code == 190 or status == 401:
        category = "BLOCKED_AUTH"
    elif code == 200 or status == 403:
        category = "PERMISSION_DENIED"
    elif code in {4, 17, 613} or status == 429:
        category = "RATE_LIMITED"
    elif code == 100 or status == 400:
        category = "FAILED_VALIDATION"
    else:
        category = "PROVIDER_ERROR"
    return MetaFailure(category, phase, code)


class MetaClient:
    def __init__(self, version: str = "v26.0", *,
                 transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        if not re.fullmatch(r"v[1-9][0-9]{0,2}\.0", version):
            raise ValueError("Invalid Graph version")
        self.version, self.sleep = version, sleep
        self.http = httpx.Client(timeout=25, transport=transport,
                                 follow_redirects=False, trust_env=False)

    def close(self) -> None:
        self.http.close()

    def graph(self, method: str, path: str, token: str, *,
              params: dict[str, str] | None = None,
              data: dict[str, str] | None = None,
              phase: str = "READ") -> dict[str, Any]:
        if not path.startswith("/") or "?" in path or "//" in path or "#" in path:
            raise ValueError("Unsafe Graph path")
        if not token:
            raise ValueError("Missing access token")
        url = f"https://graph.facebook.com/{self.version}{path}"
        headers = {"Authorization": f"Bearer {token}"}
        for attempt in range(3 if method == "GET" else 1):
            try:
                r = self.http.request(method, url, params=params, data=data, headers=headers)
            except httpx.RequestError:
                if method != "GET":
                    raise RemoteUncertain(phase) from None
                if attempt < 2:
                    self.sleep(0.25 * 2 ** attempt)
                    continue
                raise MetaFailure("TEMPORARILY_UNAVAILABLE", phase) from None
            if r.is_redirect:
                raise MetaFailure("UNEXPECTED_REDIRECT", phase)
            try:
                result = r.json()
            except ValueError:
                raise MetaFailure("MALFORMED_RESPONSE", phase) from None
            if r.is_error or (isinstance(result, dict) and "error" in result):
                err = classify(r.status_code, result, phase)
                if (method == "GET" and err.category == "RATE_LIMITED" and attempt < 2):
                    self.sleep(0.25 * 2 ** attempt)
                    continue
                raise err
            if not isinstance(result, dict):
                raise MetaFailure("MALFORMED_RESPONSE", phase)
            return result
        raise MetaFailure("TEMPORARILY_UNAVAILABLE", phase)

    def upload(self, url: str, video_id: str, token: str, path: Path) -> dict[str, Any]:
        validate_upload_url(url, video_id)
        if not path.is_file() or path.suffix.lower() != ".mp4" or path.stat().st_size <= 0:
            raise ValueError("Nonempty MP4 required")
        headers = {"Authorization": f"OAuth {token}", "offset": "0",
                   "file_size": str(path.stat().st_size),
                   "Content-Type": "application/octet-stream"}
        try:
            with path.open("rb") as f:
                r = self.http.post(url, headers=headers, content=f)
        except httpx.RequestError:
            raise RemoteUncertain("UPLOAD", video_id) from None
        if r.is_redirect:
            raise MetaFailure("UNEXPECTED_REDIRECT", "UPLOAD")
        try:
            payload = r.json()
        except ValueError:
            raise MetaFailure("MALFORMED_RESPONSE", "UPLOAD") from None
        if r.is_error or (isinstance(payload, dict) and "error" in payload):
            raise classify(r.status_code, payload, "UPLOAD")
        if not isinstance(payload, dict):
            raise MetaFailure("MALFORMED_RESPONSE", "UPLOAD")
        return payload

    def paged(self, path: str, token: str, fields: str, max_items: int = 100) -> list[dict[str, Any]]:
        if not 1 <= max_items <= 5000:
            raise ValueError("Invalid page limit")
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        after = ""
        for _ in range(50):
            params = {"fields": fields, "limit": str(min(100, max_items - len(items)))}
            if after:
                params["after"] = after
            result = self.graph("GET", path, token, params=params)
            batch = result.get("data")
            if not isinstance(batch, list) or any(not isinstance(x, dict) for x in batch):
                raise MetaFailure("MALFORMED_RESPONSE")
            items.extend(batch)
            if len(items) >= max_items:
                return items[:max_items]
            paging = result.get("paging", {})
            cursors = paging.get("cursors", {}) if isinstance(paging, dict) else {}
            next_after = cursors.get("after") if isinstance(cursors, dict) else None
            if not batch or not isinstance(next_after, str) or next_after in seen or not next_after:
                break
            seen.add(next_after)
            after = next_after
        return items
