"""MP4 metadata validation without modifying any customer content."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def inspect_mp4(path: Path, *, max_bytes: int = 1_073_741_824) -> dict[str, Any]:
    if not path.is_file() or path.suffix.lower() != ".mp4":
        raise ValueError("A readable local MP4 is required")
    size = path.stat().st_size
    if not 0 < size <= max_bytes:
        raise ValueError("MP4 size outside local P0 safety limit (not an official Meta limit)")
    with path.open("rb") as fh:
        header = fh.read(64)
    if b"ftyp" not in header[:32]:
        raise ValueError("File does not resemble an MP4 container")
    result: dict[str, Any] = {"file_size_bytes": size, "media_format": "mp4",
                              "duration_seconds": None, "width": None, "height": None,
                              "ffprobe": "UNAVAILABLE"}
    binary = shutil.which("ffprobe")
    if not binary:
        return result
    try:
        completed = subprocess.run(
            [binary, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=15, check=True)
        parsed = json.loads(completed.stdout)
        fmt = parsed.get("format", {})
        duration = float(fmt.get("duration", 0))
        video = next((s for s in parsed.get("streams", [])
                      if isinstance(s, dict) and s.get("codec_type") == "video"), None)
        if not video or duration <= 0:
            raise ValueError("MP4 has no valid video stream or duration")
        result.update({"duration_seconds": duration, "width": video.get("width"),
                       "height": video.get("height"), "ffprobe": "VALIDATED"})
    except (subprocess.SubprocessError, ValueError, TypeError, json.JSONDecodeError):
        raise ValueError("Invalid MP4 media metadata") from None
    return result

