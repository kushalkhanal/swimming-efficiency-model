"""
Blueprint for retrieving annotated video frames with skeletal overlays.
"""

from __future__ import annotations

from flask import Blueprint, Response, abort

from ..services.frame_repository import get_frame_overlay_stream

frames_bp = Blueprint("frames", __name__)


@frames_bp.get("/video-frame/<string:frame_id>")
def fetch_frame(frame_id: str) -> Response:
    """
    Stream an image containing the requested frame and its pose overlay.
    """
    stream = get_frame_overlay_stream(frame_id)

    if stream is None:
        abort(404, description="Frame not found")

    return Response(stream, mimetype="image/jpeg")

