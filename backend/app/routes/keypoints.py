"""
Blueprint for retrieving keypoints data for videos.
"""

from flask import Blueprint, jsonify, request
from ..db.repositories import FrameRepository
from ..utils.logging_config import get_logger

keypoints_bp = Blueprint("keypoints", __name__)
frame_repo = FrameRepository()
logger = get_logger(__name__)


@keypoints_bp.get("/keypoints/<string:video_id>")
def get_keypoints(video_id: str):
    """
    Get all keypoints for a video, with pagination support.
    
    Query params:
        - start: Start index (default: 0)
        - limit: Number of frames to return (default: 500)
    
    Returns:
        {
            "frames": [
                {
                    "frame_index": 0,
                    "keypoints": [[x, y, z, confidence], ...],
                    "boxes": [[x1, y1, x2, y2], ...]
                },
                ...
            ],
            "total": total_count
        }
    """
    try:
        start = int(request.args.get("start", 0))
        limit = int(request.args.get("limit", 500))
        
        # Fetch frames from database
        frames_cursor = frame_repo.collection.find(
            {"video_id": video_id},
            {"_id": False, "video_id": False}
        ).sort("frame_index", 1).skip(start).limit(limit)
        
        frames = list(frames_cursor)
        
        # Get total count for pagination
        total = frame_repo.collection.count_documents({"video_id": video_id})
        
        logger.info(f"Retrieved {len(frames)} frames for video {video_id} (start={start}, limit={limit}, total={total})")
        
        return jsonify({
            "frames": frames,
            "total": total,
            "start": start,
            "limit": limit
        })
        
    except ValueError as e:
        return jsonify({"error": "Invalid start or limit parameter"}), 400
    except Exception as e:
        logger.error(f"Error fetching keypoints for video {video_id}: {e}")
        return jsonify({"error": str(e)}), 500
