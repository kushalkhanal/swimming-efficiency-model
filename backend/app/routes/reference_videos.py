"""
Reference videos API routes.
Serves professional swimmer reference videos for comparison.
"""

from flask import Blueprint, jsonify, send_file, abort
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

reference_videos_bp = Blueprint('reference_videos', __name__)

# Base directory for reference videos
REFERENCE_VIDEOS_DIR = Path(__file__).parent.parent.parent / "data" / "reference_videos"

# Reference video metadata
REFERENCE_VIDEOS = {
    "freestyle": [],
    "backstroke": [],
    "breaststroke": [],
    "butterfly": []
}


def scan_reference_videos():
    """Scan reference_videos directory and build metadata."""
    global REFERENCE_VIDEOS
    
    if not REFERENCE_VIDEOS_DIR.exists():
        logger.warning(f"Reference videos directory not found: {REFERENCE_VIDEOS_DIR}")
        return
    
    for stroke_dir in REFERENCE_VIDEOS_DIR.iterdir():
        if not stroke_dir.is_dir():
            continue
            
        stroke = stroke_dir.name
        if stroke not in REFERENCE_VIDEOS:
            continue
        
        # Find all MP4 files in stroke directory
        video_files = list(stroke_dir.glob("*.mp4"))
        
        for video_file in video_files:
            video_id = video_file.stem  # filename without extension
            
            # Extract swimmer name from filename (e.g., "caeleb_dressel_freestyle" -> "Caeleb Dressel")
            name_parts = video_id.replace(f"_{stroke}", "").split("_")
            swimmer_name = " ".join(word.capitalize() for word in name_parts)
            
            REFERENCE_VIDEOS[stroke].append({
                "id": video_id,
                "name": f"{swimmer_name} - {stroke.capitalize()}",
                "swimmer": swimmer_name,
                "stroke": stroke,
                "videoUrl": f"/api/v1/reference-videos/{video_id}/video",
                "thumbnailUrl": f"/api/v1/reference-videos/{video_id}/thumbnail",
            })
    
    logger.info(f"Loaded reference videos: {sum(len(v) for v in REFERENCE_VIDEOS.values())} total")


@reference_videos_bp.route("/reference-videos", methods=["GET"])
def list_reference_videos():
    """Get list of all reference videos organized by stroke."""
    scan_reference_videos()  # Rescan to pick up any new videos
    return jsonify(REFERENCE_VIDEOS)


@reference_videos_bp.route("/reference-videos/<video_id>/video", methods=["GET"])
def serve_reference_video(video_id: str):
    """Serve a reference video file."""
    # Search all stroke directories for the video
    for stroke_dir in REFERENCE_VIDEOS_DIR.iterdir():
        if not stroke_dir.is_dir():
            continue
        
        video_path = stroke_dir / f"{video_id}.mp4"
        if video_path.exists() and video_path.is_file():
            return send_file(
                str(video_path),
                mimetype="video/mp4",
                as_attachment=False,
                download_name=video_path.name
            )
    
    logger.error(f"Reference video not found: {video_id}")
    abort(404, description=f"Reference video '{video_id}' not found")


@reference_videos_bp.route("/reference-videos/<video_id>/thumbnail", methods=["GET"])
def serve_reference_thumbnail(video_id: str):
    """Serve a reference video thumbnail (if available)."""
    # Search for thumbnail image
    for stroke_dir in REFERENCE_VIDEOS_DIR.iterdir():
        if not stroke_dir.is_dir():
            continue
        
        # Try different image formats
        for ext in ['.jpg', '.jpeg', '.png']:
            thumb_path = stroke_dir / f"{video_id}{ext}"
            if thumb_path.exists() and thumb_path.is_file():
                return send_file(
                    str(thumb_path),
                    mimetype=f"image/{ext[1:]}",
                    as_attachment=False
                )
    
    # No thumbnail found - return 404 or default placeholder
    abort(404, description=f"Thumbnail for '{video_id}' not found")


# Initialize on module load
scan_reference_videos()
