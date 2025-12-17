"""
Blueprint that exposes biomechanical metrics for processed videos.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.metrics_repository import get_metrics_for_video
from ..db.repositories import FrameRepository

metrics_bp = Blueprint("metrics", __name__)
frame_repo = FrameRepository()


@metrics_bp.get("/metrics/<string:video_id>")
def fetch_metrics(video_id: str):
    """
    Return all stored metrics and analytics for the supplied video identifier.
    """
    metrics = get_metrics_for_video(video_id)

    if metrics is None:
        return jsonify({"error": "Metrics not found", "video_id": video_id}), 404

    return jsonify(metrics), 200


@metrics_bp.get("/keypoints/<string:video_id>/<int:frame_index>")
def fetch_keypoints(video_id: str, frame_index: int):
    """
    Return keypoints for a specific frame.
    """
    frame_doc = frame_repo.collection.find_one({
        "_id": f"{video_id}:{frame_index}"
    })
    
    if frame_doc is None:
        return jsonify({"error": "Frame not found"}), 404
    
    return jsonify({
        "video_id": video_id,
        "frame_index": frame_index,
        "keypoints": frame_doc.get("keypoints", []),
    }), 200


@metrics_bp.get("/keypoints/<string:video_id>")
def fetch_all_keypoints(video_id: str):
    """
    Return keypoints for all frames of a video.
    Optional query params: start, limit
    """
    start = request.args.get("start", 0, type=int)
    limit = request.args.get("limit", 100, type=int)
    
    frames = list(frame_repo.collection.find(
        {"video_id": video_id},
        {"frame_index": 1, "keypoints": 1}
    ).sort("frame_index", 1).skip(start).limit(limit))
    
    if not frames:
        return jsonify({"error": "No frames found"}), 404
    
    return jsonify({
        "video_id": video_id,
        "frames": [
            {
                "frame_index": f["frame_index"],
                "keypoints": f.get("keypoints", []),
            }
            for f in frames
        ],
    }), 200

