from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from app.config import Settings
from app.p0.oauth import create_auth_url, consume_callback


def test_oauth_one_time_state(tmp_path: Path):
    s = Settings(app_id="123", redirect_uri="https://example.com/callback",
                 state_file=tmp_path / "state.json")
    url = create_auth_url(s, now=100)
    state = parse_qs(urlsplit(url).query)["state"][0]
    callback = f"https://example.com/callback?state={state}&code=example"
    assert consume_callback(s, callback, now=150) == "example"
    with pytest.raises(ValueError):
        consume_callback(s, callback, now=150)


def test_oauth_rejects_expired_state(tmp_path: Path):
    s = Settings(app_id="123", redirect_uri="https://example.com/callback",
                 state_file=tmp_path / "state.json")
    state = parse_qs(urlsplit(create_auth_url(s, now=100)).query)["state"][0]
    with pytest.raises(ValueError):
        consume_callback(s, f"https://example.com/callback?state={state}&code=x", now=701)
    assert not s.state_file.exists()

