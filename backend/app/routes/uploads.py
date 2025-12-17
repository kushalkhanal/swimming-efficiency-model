"""
Blueprint exposing endpoints for uploading raw swimming footage.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..services.video_pipeline import enqueue_video_for_processing
from ..utils.file_storage import save_upload
from ..utils.logging_config import get_logger

upload_bp = Blueprint("upload", __name__)
logger = get_logger(__name__)


@upload_bp.post("/upload-video")
def upload_video():
    """
    Accept a raw video file upload and queue it for processing.

    Returns a JSON payload containing the generated `video_id`.
    """
    try:
        if "file" not in request.files:
            logger.warning("Upload attempt with no file part")
            return jsonify({"error": "No file part in request"}), 400

        video_file = request.files["file"]
        if video_file.filename == "":
            logger.warning("Upload attempt with empty filename")
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        allowed_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v"}
        file_ext = Path(video_file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            logger.warning(f"Upload rejected: invalid extension {file_ext}")
            return jsonify({
                "error": f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            }), 400

        filename = secure_filename(video_file.filename)
        # Get upload directory from config (using UPLOAD_ROOT which is a Path)
        upload_dir: Path = Path(current_app.config["UPLOAD_ROOT"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename to avoid conflicts
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        file_stem = Path(filename).stem
        final_filename = f"{file_stem}_{unique_id}{file_ext}"
        
        logger.info(f"Saving uploaded file: {final_filename}")
        video_path = save_upload(video_file, upload_dir / final_filename)

        video_id = enqueue_video_for_processing(video_path)

        logger.info(f"Upload successful", video_id=video_id, extra_data={"filename": final_filename})
        return jsonify({
            "video_id": video_id,
            "status": "queued",
            "filename": final_filename
        }), 202

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

