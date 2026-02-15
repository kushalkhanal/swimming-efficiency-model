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
    try:
        payload = request.get_json(silent=True) or {}
        video_id: str | None = payload.get("video_id")
        start_time: float | None = payload.get("start_time")
        end_time: float | None = payload.get("end_time")
        
        # DEBUG: Log exactly what we received
        print(f"[DEBUG] /process-video received payload: {payload}")
        print(f"[DEBUG] start_time={start_time} (type={type(start_time)}), end_time={end_time} (type={type(end_time)})")

        if not video_id:
            return jsonify({"error": "video_id is required"}), 400

        # Capture the Flask app context for the background thread
        from flask import current_app
        app = current_app._get_current_object()
        
        # Run processing in background thread to avoid blocking
        import threading
        def process_in_background():
            # Push application context for database access
            with app.app_context():
                try:
                    print(f"[INFO] Starting background processing for video {video_id}")
                    status = process_video_by_id(
                        video_id,
                        start_time=start_time,
                        end_time=end_time
                    )
                    print(f"[INFO] Background processing completed with status: {status}")
                except Exception as e:
                    import traceback
                    print(f"[ERROR] Background processing failed: {str(e)}")
                    traceback.print_exc()
        
        # Start background thread
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        
        # Return immediately
        return jsonify({
            "video_id": video_id,
            "status": "processing",
            "message": "Video processing started in background"
        }), 202
    
    except Exception as e:
        # Log the full error with traceback
        import traceback
        error_msg = f"Error processing video: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()
        
        return jsonify({
            "error": error_msg,
            "details": str(e)
        }), 500

