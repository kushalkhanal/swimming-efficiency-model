"""
Blueprint for frame-level biomechanical analytics.
"""

from flask import Blueprint, jsonify
from ..db.repositories import FrameRepository
from ..services.frame_analytics import calculate_joint_angles_single_frame, rate_joint_angle
from ..utils.logging_config import get_logger
import numpy as np

frame_analytics_bp = Blueprint("frame_analytics", __name__)
frame_repo = FrameRepository()
logger = get_logger(__name__)


@frame_analytics_bp.get("/frame-analytics/<string:video_id>/<int:frame_number>")
def get_frame_analytics(video_id: str, frame_number: int):
    """
    Get biomechanical analytics for a specific frame.
    
    Returns joint angles and quality ratings for visualization.
    """
    try:
        # Fetch frame data from database
        frame_doc = frame_repo.collection.find_one({
            "video_id": video_id,
            "frame_index": frame_number
        })
        
        if not frame_doc:
            return jsonify({"error": "Frame not found"}), 404
        
        # Extract keypoints (stored as array of 33 points, each [x, y, z, confidence])
        keypoints_data = frame_doc.get("keypoints", [])
        if not keypoints_data:
            return jsonify({"error": "No keypoints data"}), 404
        
        # Convert to numpy array (33, 4)
        if not isinstance(keypoints_data, list) or len(keypoints_data) != 33:
            return jsonify({"error": "Invalid keypoints format"}), 400
            
        keypoints = np.array(keypoints_data, dtype=np.float32)
        
        # Calculate joint angles
        joint_angles = calculate_joint_angles_single_frame(keypoints)
        
        # Rate each joint
        ratings = {}
        for joint_name, angle in joint_angles.items():
            ratings[joint_name] = rate_joint_angle(angle, joint_name)
        
        return jsonify({
            "frame_number": frame_number,
            "joint_angles": joint_angles,
            "ratings": ratings
        })
        
    except Exception as e:
        logger.error(f"Error getting frame analytics: {e}", video_id=video_id)
        return jsonify({"error": str(e)}), 500
