"""
Read-only report accessors for the REST layer.
"""

from __future__ import annotations

from ..db.repositories import ReportRepository

report_repo = ReportRepository()


def fetch_report_paths(video_id: str) -> dict[str, str] | None:
    """
    Return the available report file paths for the video.
    """
    return report_repo.fetch_paths(video_id)

