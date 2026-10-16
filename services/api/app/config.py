"""Minimal typed P0 settings; no persistent credentials."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_id: str = ""
    app_secret: str = ""
    user_token: str = ""
    page_token: str = ""
    graph_version: str = "v26.0"
    redirect_uri: str = ""
    state_file: Path = Path.home() / ".facebook-reels-p0-oauth.json"

    @classmethod
    def from_env(cls) -> Settings:
        version = os.getenv("META_GRAPH_VERSION", "v26.0")
        if not re.fullmatch(r"v[1-9][0-9]{0,2}\.0", version):
            raise ValueError("Invalid META_GRAPH_VERSION")
        redirect = os.getenv("META_REDIRECT_URI", "")
        if redirect and (not redirect.startswith("https://") or "#" in redirect):
            raise ValueError("META_REDIRECT_URI must be HTTPS")
        return cls(
            app_id=os.getenv("META_APP_ID", ""),
            app_secret=os.getenv("META_APP_SECRET", ""),
            user_token=os.getenv("META_USER_TOKEN", ""),
            page_token=os.getenv("META_PAGE_TOKEN", ""),
            graph_version=version,
            redirect_uri=redirect,
            state_file=Path(os.getenv("META_OAUTH_STATE_FILE")
                            or str(Path.home() / ".facebook-reels-p0-oauth.json")),
        )

    def missing(self, *names: str) -> list[str]:
        return [name for name in names if not getattr(self, name)]

