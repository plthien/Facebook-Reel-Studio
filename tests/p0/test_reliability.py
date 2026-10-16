"""Adversarial non-live tests: no provider call is made by these tests."""
from pathlib import Path

import httpx
import pytest

from app.integrations.meta.adapter import MetaAdapter
from app.integrations.meta.client import MetaClient, MetaFailure, RemoteUncertain
from app.integrations.meta.models import Availability
from app.p0.evidence import export_evidence, journal_event, redact
from app.p0.media import inspect_mp4


def fixture_adapter(handler):
    return MetaAdapter(MetaClient(transport=httpx.MockTransport(handler), sleep=lambda _: None))


def test_ready_status_requires_processing_phase_complete():
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(200, json={"status": {"processing_phase": {"status": "complete"}}})
    a = fixture_adapter(handler)
    assert a.wait_for_upload_ready("123", "token", interval=0)["ready"]
    assert len(calls) == 1


def test_unknown_processing_status_never_finishes():
    a = fixture_adapter(lambda request: httpx.Response(200, json={"status": {"video_status": "ready"}}))
    with pytest.raises(RemoteUncertain) as exc:
        a.wait_for_upload_ready("123", "token")
    assert exc.value.phase == "STATUS"


def test_pending_processing_stops_at_bound():
    calls = []
    def handler(request):
        calls.append(1)
        return httpx.Response(200, json={"status": {"processing_phase": {"status": "in_progress"}}})
    a = fixture_adapter(handler)
    with pytest.raises(RemoteUncertain) as exc:
        a.wait_for_upload_ready("123", "token", max_checks=3, interval=0)
    assert exc.value.phase == "PROCESSING"
    assert len(calls) == 3


def test_failed_processing_stops():
    a = fixture_adapter(lambda request: httpx.Response(
        200, json={"status": {"processing_phase": {"status": "failed"}}}))
    with pytest.raises(MetaFailure) as exc:
        a.wait_for_upload_ready("123", "token")
    assert exc.value.category == "PROCESSING_FAILED"


def test_video_identity_fail_closed():
    a = fixture_adapter(lambda request: httpx.Response(
        200, json={"id": "123", "from": {"id": "wrong"},
                   "status": {"video_status": "published"}}))
    result = a.verify_published_reel("42", "123", "token")
    assert not result.publication_verified


def test_missing_views_never_synthesized():
    a = fixture_adapter(lambda request: httpx.Response(400, json={"error": {"code": 100}}))
    result = a.probe_insights("123", "token", object_type="POST")
    assert result.availability == Availability.UNVERIFIED
    assert result.value is None


def test_redaction_nested_and_evidence_permissions(tmp_path: Path):
    payload = {"access_token": "do-not-leak", "safe": {"Authorization": "Bearer do-not-leak"},
               "nested": ["access_token=bad&visible=yes"]}
    output = redact(payload)
    assert "do-not-leak" not in str(output)
    assert "access_token=bad" not in str(output)
    path = journal_event(tmp_path, phase="START", page_id="123", video_id="456",
                         extra={"upload_url": "https://rupload.facebook.com/video-upload/456?secret=x"})
    assert path.stat().st_mode & 0o077 == 0
    exported = export_evidence(tmp_path)
    assert exported["events"][0]["video_id"] == "456"
    assert "secret=x" not in str(exported)


def test_invalid_mp4_rejected_locally(tmp_path: Path):
    f = tmp_path / "fake.mp4"
    f.write_bytes(b"not an MP4")
    with pytest.raises(ValueError):
        inspect_mp4(f)

