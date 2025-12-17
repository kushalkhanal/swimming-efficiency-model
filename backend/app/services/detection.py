"""
Swimmer detection utilities leveraging open-source object detection models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

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
        results = self.model.predict(frame, imgsz=640, conf=0.5, device="cpu")
        boxes: List[tuple[int, int, int, int]] = []
        for result in results:
            for box in result.boxes.xyxy.cpu().numpy():
                x1, y1, x2, y2 = box.astype(int)
                boxes.append((x1, y1, x2 - x1, y2 - y1))
        return boxes


def detect_swimmers(
    video_path: Path,
    start_time_seconds: float = 0.0,
    max_duration_seconds: float = 300.0,
    sample_every_n_frames: int = 2,
) -> list[DetectedFrame]:
    """
    Iterate through the video and perform swimmer detection on each frame.

    Args:
        video_path: Path to the video file
        start_time_seconds: Start processing from this time (default: 0)
        max_duration_seconds: Process for this many seconds (default: 60)
        sample_every_n_frames: Process every Nth frame for speed (default: 2)
    
    The current implementation processes frames sequentially with optional
    sampling and duration limits for faster processing.
    """
    if YOLO is None:
        raise RuntimeError(
            "YOLOv8 not installed. Detection step cannot run in this environment."
        )

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

    # Seek to start frame
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames: list[DetectedFrame] = []

    frame_index = start_frame
    try:
        while frame_index < end_frame:
            success, image = cap.read()
            if not success:
                break

            # Sample frames for faster processing
            if (frame_index - start_frame) % sample_every_n_frames == 0:
                boxes = detector.detect(image)
                frames.append(DetectedFrame(frame_index=frame_index, image=image, boxes=boxes))
            
            frame_index += 1
    finally:
        cap.release()

    print(f"Processed {len(frames)} frames")
    return frames

