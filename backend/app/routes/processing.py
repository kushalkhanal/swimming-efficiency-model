"""
Blueprint containing endpoints to trigger and inspect processing workflows.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.video_pipeline import process_video_by_id

processing_bp = Blueprint("processing", __name__)


@processing_bp.post("/process-video")
def process_video():
    """
    Kick off the full analysis pipeline for a video that was previously uploaded.

    The request body should contain:
    - video_id: Reference to the uploaded video (required)
    - start_time: Start time in seconds for analysis (optional)
    - end_time: End time in seconds for analysis (optional)
    """
    payload = request.get_json(silent=True) or {}
    video_id: str | None = payload.get("video_id")
    start_time: float | None = payload.get("start_time")
    end_time: float | None = payload.get("end_time")
    
    # DEBUG: Log exactly what we received
    print(f"[DEBUG] /process-video received payload: {payload}")
    print(f"[DEBUG] start_time={start_time} (type={type(start_time)}), end_time={end_time} (type={type(end_time)})")

    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    job_status = process_video_by_id(
        video_id,
        start_time=start_time,
        end_time=end_time
    )

    return jsonify({"video_id": video_id, "status": job_status}), 202

