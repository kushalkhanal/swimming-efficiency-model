"""
High-level orchestration for the end-to-end video analysis pipeline.
"""

from __future__ import annotations

import uuid
import time
from pathlib import Path

from ..db.repositories import FrameRepository, MetricsRepository, VideoRepository
from ..utils.logging_config import get_logger
from .detection import detect_swimmers
from .pose_estimation import extract_poses_2d, estimate_poses_3d
from .analytics import (
    compute_biomechanics_metrics,
    generate_narrative_feedback,
    segment_stroke_phases,
)
from .reporting import generate_report_artifacts
from .coaching_feedback import (
    generate_timeline_feedback,
    generate_plain_language_metrics,
    generate_coaching_summary,
)

logger = get_logger(__name__)

# Repository singletons (could be dependency-injected in the future)
video_repo = VideoRepository()
metrics_repo = MetricsRepository()
frame_repo = FrameRepository()


def emit_progress(video_id: str, stage: str, progress: float, message: str = ""):
    """Emit processing progress via WebSocket."""
    try:
        from .. import get_socketio
        socketio = get_socketio()
        socketio.emit("processing_progress", {
            "video_id": video_id,
            "stage": stage,
            "progress": progress,
            "message": message
        })
        logger.debug(f"Progress: {stage} {progress}%", video_id=video_id)
    except Exception as e:
        logger.warning(f"Failed to emit progress: {e}", video_id=video_id)


def enqueue_video_for_processing(video_path: Path) -> str:
    """
    Persist initial metadata and return a `video_id` for downstream processing.

    A production implementation could push this into a task queue; in this
    skeleton we simply record the upload and return the identifier.
    """
    video_id = uuid.uuid4().hex
    video_repo.insert_video(video_id, {"path": str(video_path), "status": "pending"})
    logger.info(f"Video queued for processing", video_id=video_id, extra_data={"path": str(video_path)})
    return video_id


def process_video_by_id(
    video_id: str,
    start_time: float | None = None,
    end_time: float | None = None
) -> str:
    """
    Run the full video analytics pipeline with real-time progress updates.
    
    Args:
        video_id: The ID of the video to process
        start_time: Start time in seconds (optional, defaults to 0)
        end_time: End time in seconds (optional, defaults to start_time + 60)
    """
    pipeline_start = time.time()
    logger.info(
        "Starting video processing pipeline",
        video_id=video_id,
        extra_data={"start_time": start_time, "end_time": end_time}
    )
    
    video_doc = video_repo.fetch_video(video_id)
    if video_doc is None:
        logger.error("Video not found in database", video_id=video_id)
        emit_progress(video_id, "detection", 0, "Video not found")
        return "not_found"

    video_path = Path(video_doc["path"])
    
    # Calculate trim parameters
    trim_start = start_time if start_time is not None else 0.0
    trim_duration = (end_time - trim_start) if end_time is not None else 300.0  # Default 5 min if no end specified
    
    # DEBUG: Log trim calculation
    print(f"[DEBUG] Pipeline trim calculation:")
    print(f"[DEBUG]   start_time param: {start_time}")
    print(f"[DEBUG]   end_time param: {end_time}")
    print(f"[DEBUG]   trim_start: {trim_start}")
    print(f"[DEBUG]   trim_duration: {trim_duration}")
    
    # Stage 1: Detection (0-20%)
    emit_progress(video_id, "detection", 5, f"Analyzing {trim_duration:.1f}s segment...")
    frames = detect_swimmers(
        video_path,
        start_time_seconds=trim_start,
        max_duration_seconds=trim_duration
    )
    emit_progress(video_id, "detection", 20, f"Detected {len(frames)} frames")

    # Stage 2: Pose Estimation (20-50%)
    emit_progress(video_id, "pose", 25, "Extracting 2D poses...")
    poses2d = extract_poses_2d(frames)
    emit_progress(video_id, "pose", 40, "Estimating 3D poses...")
    poses3d = estimate_poses_3d(poses2d)
    emit_progress(video_id, "pose", 50, "Pose estimation complete")

    # Stage 3: Metrics Computation (50-75%)
    emit_progress(video_id, "metrics", 55, "Computing biomechanics metrics...")
    
    # Get video FPS for accurate calculations
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()
    
    metrics = compute_biomechanics_metrics(poses2d, poses3d, fps=fps)
    emit_progress(video_id, "metrics", 65, "Segmenting stroke phases...")
    stroke_phases = segment_stroke_phases(poses2d, metrics)
    emit_progress(video_id, "metrics", 70, "Generating feedback...")
    narrative = generate_narrative_feedback(metrics, stroke_phases)
    
    # Generate coaching-focused feedback
    emit_progress(video_id, "metrics", 72, "Generating coaching insights...")
    timeline_segments = generate_timeline_feedback(metrics, fps=fps)
    plain_metrics = generate_plain_language_metrics(metrics)
    coaching_summary = generate_coaching_summary(metrics, timeline_segments, plain_metrics)
    
    # Merge coaching summary into narrative
    narrative["coaching"] = coaching_summary
    emit_progress(video_id, "metrics", 75, "Metrics computation complete")

    # Stage 4: Storage (75-85%)
    emit_progress(video_id, "report", 78, "Storing metrics...")
    metrics_repo.store_metrics(
        video_id,
        metrics=metrics,
        stroke_phases=stroke_phases,
        narrative=narrative,
    )

    emit_progress(video_id, "report", 82, "Storing frames...")
    frame_repo.store_frames(video_id, frames, poses2d)

    # Stage 5: Report Generation (85-100%)
    emit_progress(video_id, "report", 88, "Generating report artifacts...")
    generate_report_artifacts(
        video_id=video_id,
        video_path=video_path,
        metrics=metrics,
        narrative=narrative,
    )

    emit_progress(video_id, "report", 95, "Finalizing...")
    video_repo.update_status(video_id, status="processed")
    emit_progress(video_id, "report", 100, "Processing complete!")
    
    pipeline_duration = time.time() - pipeline_start
    logger.info(
        "Video processing completed",
        video_id=video_id,
        extra_data={"duration_seconds": round(pipeline_duration, 2), "frames_processed": len(frames)}
    )
    
    return "processed"

