from pathlib import Path

import httpx
import pytest

from app.integrations.meta.adapter import MetaAdapter
from app.integrations.meta.client import MetaClient, MetaFailure, RemoteUncertain, validate_upload_url
from app.integrations.meta.models import Availability, PublicationState


def client(handler):
    return MetaClient(transport=httpx.MockTransport(handler), sleep=lambda _: None)


def test_page_pagination_and_tokens_not_in_safe_output():
    def handler(request):
        if "after=" in str(request.url):
            return httpx.Response(200, json={"data": [{"id": "999999999999999999", "name": "B",
                                                       "access_token": "secret-b", "tasks": []}]})
        return httpx.Response(200, json={"data": [{"id": "123", "name": "A", "access_token": "secret-a",
                                                   "tasks": ["CREATE_CONTENT"]}],
                                          "paging": {"cursors": {"after": "next"}}})
    adapter = MetaAdapter(client(handler))
    pages = adapter.pages("user-secret")
    assert len(pages) == 2
    assert pages[1].id == "999999999999999999"
    assert "secret" not in str([p.safe() for p in pages])


def test_untrusted_upload_hosts():
    for url in ("http://rupload.facebook.com/video-upload/123",
                "https://evil.example/video-upload/123",
                "https://rupload.facebook.com.evil.net/video-upload/123",
                "https://rupload.facebook.com/video-upload/123?key=secret",
                "https://user:pass@rupload.facebook.com/video-upload/123"):
        with pytest.raises(ValueError):
            validate_upload_url(url, "123")


def test_start_and_finish_do_not_prove_publication():
    def handler(request):
        if request.method == "POST" and b"start" in request.content:
            return httpx.Response(200, json={"video_id": "123",
                                               "upload_url": "https://rupload.facebook.com/video-upload/123"})
        if request.method == "POST":
            return httpx.Response(200, json={"success": True})
        return httpx.Response(200, json={"id": "123", "from": {"id": "88"},
                                         "status": {"video_status": "processing"}})
    adapter = MetaAdapter(client(handler))
    session = adapter.start_reel_upload("88", "page-secret")
    assert session.video_id == "123"
    assert adapter.finish_reel_publish("88", "123", "page-secret", "title", "caption")
    mapping = adapter.verify_published_reel("88", "123", "page-secret")
    assert not mapping.publication_verified
    assert mapping.state == PublicationState.UNCERTAIN


def test_finish_timeout_not_replayed():
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("secret-should-not-leak")
    adapter = MetaAdapter(client(handler))
    with pytest.raises(RemoteUncertain) as caught:
        adapter.finish_reel_publish("1", "2", "secret", "title", "caption")
    assert caught.value.phase == "FINISH"
    assert len(calls) == 1
    assert "secret" not in str(caught.value)


def test_reel_insights_zero_is_valid_but_missing_is_not():
    adapter = MetaAdapter(client(lambda request: httpx.Response(
        200, json={"data": [{"name": "post_media_view", "values": [{"value": 0}]}]})))
    zero = adapter.probe_insights("23", "token", object_type="POST")
    assert zero.availability == Availability.SUPPORTED and zero.value == 0
    missing = MetaAdapter(client(lambda request: httpx.Response(200, json={"data": []})))
    metric = missing.probe_insights("23", "token", object_type="POST")
    assert metric.value is None and metric.availability == Availability.UNVERIFIED


def test_page_views_not_substituted_for_reel_views():
    adapter = MetaAdapter(client(lambda request: httpx.Response(200, json={"data": []})))
    result = adapter.probe_insights("23", "token", object_type="POST", metric="page_media_view")
    assert result.availability == Availability.NOT_APPLICABLE


def test_read_rate_limit_bounded():
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(429, json={"error": {"code": 613}})
    with pytest.raises(MetaFailure):
        client(handler).graph("GET", "/123", "token")
    assert len(calls) == 3


def test_upload_stream_sends_auth_and_size(tmp_path: Path):
    content = tmp_path / "x.mp4"
    content.write_bytes(b"test-media")
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"success": True})
    result = client(handler).upload("https://rupload.facebook.com/video-upload/123", "123", "token", content)
    assert result["success"] is True
    assert calls[0].headers["file_size"] == "10"
    assert calls[0].headers["authorization"] == "OAuth token"

