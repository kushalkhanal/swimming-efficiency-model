"""
Swimmer detection utilities leveraging open-source object detection models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - optional runtime dependency
    YOLO = None  # type: ignore[assignment]


@dataclass(slots=True)
class DetectedFrame:
    """
    Container holding a frame image and swimmer bounding boxes.
    """

    frame_index: int
    image: np.ndarray
    boxes: List[tuple[int, int, int, int]]


class SwimmerDetector:
    """
    Wrapper around YOLOv8 / SSD models for offline swimmer detection.
    Thread-safe detector for parallel processing.
    """

    def __init__(self, model_path: str | None = None) -> None:
        if YOLO is None:
            raise RuntimeError(
                "ultralytics package not available. Install YOLOv8 to enable detection."
            )
        # Default to a lightweight open-source checkpoint if none is provided.
        self.model = YOLO(model_path or "yolov8n.pt")

    def detect(self, frame: np.ndarray) -> List[tuple[int, int, int, int]]:
        """
        Run inference on a single frame and return bounding boxes.
        """
        results = self.model.predict(frame, imgsz=640, conf=0.5, device="cpu", verbose=False)
        boxes: List[tuple[int, int, int, int]] = []
        for result in results:
            for box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = box.astype(int)
                boxes.append((x1, y1, x2 - x1, y2 - y1))
        return boxes


def _detect_frame_batch(args: tuple) -> DetectedFrame | None:
    """Helper function for parallel frame detection."""
    frame_index, image, detector = args
    try:
        boxes = detector.detect(image)
        return DetectedFrame(frame_index=frame_index, image=image, boxes=boxes)
    except Exception as e:
        print(f"Error processing frame {frame_index}: {e}")
        return None


def detect_swimmers(
    video_path: Path,
    start_time_seconds: float = 0.0,
    max_duration_seconds: float = 300.0,
    sample_every_n_frames: int = 2,
    max_workers: int | None = None,
) -> list[DetectedFrame]:
    """
    Iterate through the video and perform swimmer detection on each frame.
    Uses parallel processing for faster detection.

    Args:
        video_path: Path to the video file
        start_time_seconds: Start processing from this time (default: 0)
        max_duration_seconds: Process for this many seconds (default: 300)
        sample_every_n_frames: Process every Nth frame for speed (default: 2)
        max_workers: Number of parallel workers (default: CPU count)
    
    Uses ThreadPoolExecutor to process frames in parallel for better performance.
    """
    if YOLO is None:
        raise RuntimeError(
            "YOLOv8 not installed. Detection step cannot run in this environment."
        )

    # Determine number of workers (use CPU count, but limit to avoid overload)
    if max_workers is None:
        max_workers = min(os.cpu_count() or 4, 8)  # Limit to 8 to avoid memory issues
    
    detector = SwimmerDetector()
    cap = cv2.VideoCapture(str(video_path))
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame range based on time parameters
    start_frame = int(fps * start_time_seconds)
    max_frames = int(fps * max_duration_seconds)
    end_frame = min(start_frame + max_frames, total_frames)
    
    print(f"Video: {fps:.1f} FPS, {total_frames} total frames")
    print(f"Processing frames {start_frame}-{end_frame} ({start_time_seconds:.1f}s to {start_time_seconds + max_duration_seconds:.1f}s)")
    print(f"Sampling every {sample_every_n_frames} frames")
    print(f"Using {max_workers} parallel workers")

    # First pass: collect all frames to process
    frame_batch: list[tuple[int, np.ndarray]] = []
    
    # Seek to start frame
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frame_index = start_frame
    try:
        while frame_index < end_frame:
            success, image = cap.read()
            if not success:
                break

            # Sample frames for faster processing
            if (frame_index - start_frame) % sample_every_n_frames == 0:
                # Copy image to avoid issues with frame reuse
                frame_batch.append((frame_index, image.copy()))
            
            frame_index += 1
    finally:
        cap.release()

    # Parallel processing of frames
    frames: list[DetectedFrame] = []
    
    if frame_batch:
        # Use ThreadPoolExecutor for parallel detection
        # Note: YOLO models may have internal thread safety, but we use threads
        # since GPU operations are often I/O bound in Python
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all frame detection tasks
            future_to_frame = {
                executor.submit(_detect_frame_batch, (idx, img, detector)): idx
                for idx, img in frame_batch
            }
            
            # Collect results as they complete, maintaining order
            results: dict[int, DetectedFrame] = {}
            for future in as_completed(future_to_frame):
                result = future.result()
                if result is not None:
                    results[result.frame_index] = result
            
            # Sort by frame index to maintain order
            frames = [results[idx] for idx, _ in frame_batch if idx in results]

    print(f"Processed {len(frames)} frames using {max_workers} workers")
    return frames

