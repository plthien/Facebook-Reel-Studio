"""P0 Graph adapter: all provider-specific assumptions are live-unverified."""
from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import Any

from app.integrations.meta.client import MetaClient, MetaFailure, RemoteUncertain, numeric_id
from app.integrations.meta.models import (
    Availability,
    MetricResult,
    Page,
    PublicationState,
    ReelMapping,
    UploadSession,
    observed_at,
)


class MetaAdapter:
    def __init__(self, client: MetaClient):
        self.client = client

    def pages(self, user_token: str) -> list[Page]:
        rows = self.client.paged("/me/accounts", user_token, "id,name,access_token,tasks", 100)
        result = []
        for row in rows:
            token, pid = row.get("access_token"), row.get("id")
            if not isinstance(token, str) or not isinstance(pid, str):
                continue
            result.append(Page(numeric_id(pid), str(row.get("name", "")),
                               tuple(str(x) for x in row.get("tasks", [])), token))
        return result

    def page_health(self, page_id: str, token: str) -> Page:
        pid = numeric_id(page_id)
        result = self.client.graph("GET", f"/{pid}", token, params={"fields": "id,name"})
        if result.get("id") != pid:
            raise MetaFailure("PAGE_IDENTITY_MISMATCH")
        return Page(pid, str(result.get("name", "")), (), token, verified=True)

    def list_reels(self, page_id: str, token: str, limit: int = 100) -> list[dict[str, Any]]:
        return self.client.paged(f"/{numeric_id(page_id)}/video_reels", token, "id,description,created_time", limit)

    def inspect_reel(self, video_id: str, token: str) -> dict[str, Any]:
        return self.client.graph("GET", f"/{numeric_id(video_id)}", token,
                                 params={"fields": "id,status,permalink_url,post_id,from"})

    def start_reel_upload(self, page_id: str, token: str,
                          route: str = "page") -> UploadSession:
        if route not in {"page", "me"}:
            raise ValueError("Unknown upload route")
        endpoint = f"/{numeric_id(page_id)}/video_reels" if route == "page" else "/me/video_reels"
        data = self.client.graph("POST", endpoint, token,
                                 data={"upload_phase": "start"}, phase="START")
        video_id, url = data.get("video_id"), data.get("upload_url")
        if not isinstance(video_id, str) or not isinstance(url, str):
            raise MetaFailure("MALFORMED_RESPONSE", "START")
        numeric_id(video_id)
        from app.integrations.meta.client import validate_upload_url
        validate_upload_url(url, video_id)
        return UploadSession(video_id, url)

    def upload_local_reel(self, session: UploadSession, token: str, path: Path) -> dict[str, Any]:
        return self.client.upload(session.upload_url, session.video_id, token, path)

    def get_upload_status(self, video_id: str, token: str) -> dict[str, Any]:
        return self.client.graph("GET", f"/{numeric_id(video_id)}", token,
                                 params={"fields": "status"})

    def wait_for_upload_ready(self, video_id: str, token: str, *,
                              max_checks: int = 12, interval: float = 5,
                              monotonic: Callable[[], float] | None = None,
                              max_elapsed_seconds: float = 120) -> dict[str, Any]:
        """Fail closed on unknown, failed, or not-yet-complete processing status."""
        import time

        if not 1 <= max_checks <= 60 or not 0 <= interval <= 300 or max_elapsed_seconds <= 0:
            raise ValueError("Invalid polling bounds")
        clock = monotonic or time.monotonic
        deadline = clock() + max_elapsed_seconds
        for attempt in range(max_checks):
            data = self.get_upload_status(video_id, token)
            status = data.get("status")
            phase = status.get("processing_phase") if isinstance(status, dict) else None
            phase_status = str(phase.get("status", "")).lower() if isinstance(phase, dict) else ""
            if phase_status in {"complete", "completed"}:
                return {"video_id": video_id, "ready": True, "method": "processing_phase"}
            if phase_status in {"error", "failed"}:
                raise MetaFailure("PROCESSING_FAILED", "STATUS")
            if not phase_status:
                raise RemoteUncertain("STATUS", video_id)
            if attempt + 1 < max_checks:
                if clock() + interval > deadline:
                    break
                self.client.sleep(interval)
        raise RemoteUncertain("PROCESSING", video_id)

    def finish_reel_publish(self, page_id: str, video_id: str, token: str,
                            title: str, description: str, route: str = "page") -> bool:
        endpoint = f"/{numeric_id(page_id)}/video_reels" if route == "page" else "/me/video_reels"
        data = self.client.graph("POST", endpoint, token,
                                 data={"upload_phase": "finish", "video_id": numeric_id(video_id),
                                       "video_state": "PUBLISHED", "title": title,
                                       "description": description}, phase="FINISH")
        return data.get("success") is True  # NEVER proof of a published Reel

    def verify_published_reel(self, page_id: str, video_id: str, token: str) -> ReelMapping:
        pid, vid = numeric_id(page_id), numeric_id(video_id)
        data = self.inspect_reel(vid, token)
        status = data.get("status", {})
        status_text = str(status.get("video_status", "")).lower() if isinstance(status, dict) else ""
        source = data.get("from", {})
        owner = source.get("id") if isinstance(source, dict) else None
        # Provider field semantics must be confirmed in authorized live testing.
        verified = (data.get("id") == vid and owner == pid and
                    status_text in {"published", "published_to_page"})
        post_id = data.get("post_id")
        permalink = data.get("permalink_url")
        return ReelMapping(page_id=pid, fb_video_id=vid,
                           fb_post_id=post_id if isinstance(post_id, str) else None,
                           permalink=permalink if isinstance(permalink, str) else None,
                           publication_verified=verified,
                           verification_method="video_object_status_and_page" if verified else None,
                           verified_at=observed_at() if verified else None,
                           state=PublicationState.VERIFIED_PUBLISHED if verified else PublicationState.UNCERTAIN)

    def reconcile_reel(self, page_id: str, video_id: str, token: str) -> ReelMapping:
        return self.verify_published_reel(page_id, video_id, token)

    def probe_insights(self, object_id: str, token: str, *,
                       object_type: str, metric: str = "post_media_view") -> MetricResult:
        if object_type not in {"POST", "PAGE", "VIDEO"}:
            raise ValueError("Invalid object type")
        if object_type == "PAGE" and metric == "post_media_view":
            return MetricResult(metric, object_type, numeric_id(object_id),
                                Availability.NOT_APPLICABLE, graph_version=self.client.version)
        if object_type != "PAGE" and metric == "page_media_view":
            return MetricResult(metric, object_type, numeric_id(object_id),
                                Availability.NOT_APPLICABLE, graph_version=self.client.version)
        try:
            result = self.client.graph("GET", f"/{numeric_id(object_id)}/insights", token,
                                       params={"metric": metric, **({"period": "day"} if object_type == "PAGE" else {})})
        except MetaFailure as ex:
            category = (Availability.PERMISSION_DENIED if ex.category in {"BLOCKED_AUTH", "PERMISSION_DENIED"}
                        else Availability.UNSUPPORTED if ex.category == "FAILED_VALIDATION"
                        else Availability.TEMPORARILY_UNAVAILABLE)
            return MetricResult(metric, object_type, object_id, category, graph_version=self.client.version, error_code=ex.code)
        rows = result.get("data")
        value = None
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict) or row.get("name") != metric:
                    continue
                vals = row.get("values")
                if isinstance(vals, list) and vals and isinstance(vals[0], dict):
                    candidate = vals[0].get("value")
                    if isinstance(candidate, int) and not isinstance(candidate, bool) and candidate >= 0:
                        value = candidate
        return MetricResult(metric, object_type, object_id,
                            Availability.SUPPORTED if value is not None else Availability.UNVERIFIED,
                            value=value, collected_at=observed_at() if value is not None else None,
                            graph_version=self.client.version)
