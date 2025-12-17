"""
Service helpers for retrieving frame overlays from MongoDB and local storage.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from ..db.repositories import FrameRepository

frame_repo = FrameRepository()


def get_frame_overlay_stream(frame_id: str) -> Optional[bytes]:
    """
    Compose an image response for the requested frame and pose overlay.

    Currently this function simply returns the stored image buffer placeholder.
    A production implementation would load the raw frame, draw skeleton lines,
    and encode to JPEG.
    """
    frame_doc = frame_repo.fetch_frame(frame_id)
    if frame_doc is None:
        return None

    # Placeholder: return an empty white image; real implementation draws skeleton.
    image = 255 * np.ones((480, 854, 3), dtype=np.uint8)
    success, buffer = cv2.imencode(".jpg", image)
    if not success:
        return None
    return buffer.tobytes()

