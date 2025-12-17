"""
Dataclasses describing video metadata and processing results.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class VideoMetadata:
    video_id: str
    path: Path
    status: str
    uploaded_at: datetime
    frame_rate: float | None = None
    resolution: tuple[int, int] | None = None
    extra: dict[str, Any] | None = None

