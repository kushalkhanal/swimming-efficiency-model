"""
Routes for serving video files to the frontend.
"""

from pathlib import Path
from flask import Blueprint, send_file, current_app, abort
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

videos_bp = Blueprint("videos", __name__)


@videos_bp.route("/videos/<video_id>", methods=["GET"])
def serve_video(video_id: str):
    """
    Serve a video file by ID from the uploads directory.
    
    Args:
        video_id: The video identifier (can be full filename or ID)
    
    Returns:
        Video file with appropriate MIME type
    """
    try:
        # Get the uploads directory path
        uploads_dir = Path(current_app.config.get("UPLOAD_DIR", "data/uploads"))
        
        # Try to find the video file
        # First, try as exact filename
        video_path = uploads_dir / video_id
        
        if not video_path.exists():
            # Try with .mp4 extension if not provided
            if not video_id.endswith('.mp4'):
                video_path = uploads_dir / f"{video_id}.mp4"
        
        if not video_path.exists():
            # Try to find by pattern (for videos with suffixes like _abc123ef.mp4)
            matching_files = list(uploads_dir.glob(f"*{video_id}*.mp4"))
            if matching_files:
                video_path = matching_files[0]
            else:
                logger.warning(f"Video not found: {video_id}")
                abort(404, description=f"Video '{video_id}' not found")
        
        # Ensure the file exists and is actually a file
        if not video_path.is_file():
            logger.warning(f"Path exists but is not a file: {video_path}")
            abort(404, description=f"Video '{video_id}' not found")
        
        # Log successful access
        logger.info(f"Serving video: {video_path.name}", extra_data={"video_id": video_id})
        
        # Send the file with appropriate MIME type
        return send_file(
            str(video_path),
            mimetype="video/mp4",
            as_attachment=False,
            download_name=video_path.name
        )
    
    except Exception as e:
        logger.error(f"Error serving video {video_id}: {str(e)}", exc_info=True)
        abort(500, description="Error serving video file")
