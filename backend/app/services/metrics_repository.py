"""
Service layer wrapping metrics repository access.
"""

from __future__ import annotations

from ..db.repositories import MetricsRepository

metrics_repo = MetricsRepository()


def get_metrics_for_video(video_id: str) -> dict | None:
    """
    Retrieve serialized metrics for the given video id.
    """
    return metrics_repo.fetch_metrics(video_id)

