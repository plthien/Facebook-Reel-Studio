"""Provider-safe response models."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class PublicationState(StrEnum):
    UPLOAD_STARTED = "UPLOAD_STARTED"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    FINISH_REQUESTED = "FINISH_REQUESTED"
    VERIFYING = "VERIFYING"
    VERIFIED_PUBLISHED = "VERIFIED_PUBLISHED"
    FAILED = "FAILED"
    UNCERTAIN = "UNCERTAIN"


class Availability(StrEnum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class Page:
    id: str
    name: str
    tasks: tuple[str, ...]
    access_token: str
    verified: bool = False

    def safe(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "tasks": list(self.tasks),
                "verified": self.verified}


@dataclass(frozen=True)
class UploadSession:
    video_id: str
    upload_url: str
    state: PublicationState = PublicationState.UPLOAD_STARTED

    def safe(self) -> dict[str, str]:
        return {"video_id": self.video_id, "state": self.state.value}


@dataclass(frozen=True)
class ReelMapping:
    page_id: str
    fb_video_id: str
    fb_post_id: str | None = None
    permalink: str | None = None
    publication_verified: bool = False
    verification_method: str | None = None
    verified_at: str | None = None
    state: PublicationState = PublicationState.UNCERTAIN

    def safe(self) -> dict[str, Any]:
        result = asdict(self)
        result["state"] = self.state.value
        return result


@dataclass(frozen=True)
class MetricResult:
    metric_key: str
    object_type: str
    object_id: str
    availability: Availability = Availability.UNVERIFIED
    value: int | None = None
    collected_at: str | None = None
    graph_version: str = "v26.0"
    error_code: int | None = None

    def safe(self) -> dict[str, Any]:
        result = asdict(self)
        result["availability"] = self.availability.value
        return result


def observed_at() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
