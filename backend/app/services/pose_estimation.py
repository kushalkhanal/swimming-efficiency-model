"""
Pose estimation utilities built on MediaPipe and optional VideoPose3D.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import numpy as np

from .detection import DetectedFrame

try:
    import mediapipe as mp
except ImportError:  # pragma: no cover - optional dependency
    mp = None  # type: ignore[assignment]

try:
    # VideoPose3D is optional and only used when available.
    from common.model import TemporalModel  # type: ignore import
except ImportError:  # pragma: no cover - optional dependency
    TemporalModel = None  # type: ignore[assignment]


@dataclass(slots=True)
class Pose2DResult:
    """
    2D pose estimation result in image coordinates.
    """

    frame_index: int
    keypoints: np.ndarray  # Shape: (33, 4) -> x, y, z(abs depth), visibility


@dataclass(slots=True)
class Pose3DResult:
    """
    Optional 3D pose estimation result in canonical coordinates.
    """

    frame_index: int
    keypoints: np.ndarray  # Shape: (33, 3) -> x, y, z


def _build_mediapipe_solution():
    if mp is None:
        raise RuntimeError(
            "MediaPipe is not installed. Install mediapipe to enable pose estimation."
        )
    mp_pose = mp.solutions.pose
    return mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def _process_frame_pose(args: tuple) -> Pose2DResult | None:
    """Helper function for parallel pose estimation."""
    detected, pose = args
    try:
        mp_result = pose.process(detected.image[:, :, ::-1])  # BGR -> RGB
        if not mp_result.pose_landmarks:
            return None

        keypoints = np.array(
            [
                [
                    landmark.x,
                    landmark.y,
                    landmark.z,
                    landmark.visibility,
                ]
                for landmark in mp_result.pose_landmarks.landmark
            ],
            dtype=np.float32,
        )

        return Pose2DResult(frame_index=detected.frame_index, keypoints=keypoints)
    except Exception as e:
        print(f"Error processing pose for frame {detected.frame_index}: {e}")
        return None


def extract_poses_2d(frames: Iterable[DetectedFrame], max_workers: int | None = None) -> list[Pose2DResult]:
    """
    Run MediaPipe Pose on each frame and return 33-keypoint landmarks.
    Uses parallel processing for better performance.
    
    Args:
        frames: Iterable of DetectedFrame objects
        max_workers: Number of parallel workers (default: CPU count)
    """
    frames_list = list(frames)
    if not frames_list:
        return []
    
    # Determine number of workers
    if max_workers is None:
        max_workers = min(os.cpu_count() or 4, 8)  # Limit to 8
    
    pose_solution = _build_mediapipe_solution()
    results: list[Pose2DResult] = []

    # MediaPipe Pose solution needs to be shared across threads
    # Each thread will create its own pose processor
    def process_batch(frame_batch: list[DetectedFrame]) -> list[Pose2DResult]:
        """Process a batch of frames with a single pose processor."""
        batch_results = []
        pose = _build_mediapipe_solution()
        try:
            for detected in frame_batch:
                mp_result = pose.process(detected.image[:, :, ::-1])  # BGR -> RGB
                if not mp_result.pose_landmarks:
                    continue

                keypoints = np.array(
                    [
                        [
                            landmark.x,
                            landmark.y,
                            landmark.z,
                            landmark.visibility,
                        ]
                        for landmark in mp_result.pose_landmarks.landmark
                    ],
                    dtype=np.float32,
                )

                batch_results.append(Pose2DResult(frame_index=detected.frame_index, keypoints=keypoints))
        finally:
            pose.close()
        return batch_results
    
    # Process frames in parallel batches
    # Split frames into batches for better memory management
    batch_size = max(1, len(frames_list) // max_workers)
    batches = [frames_list[i:i + batch_size] for i in range(0, len(frames_list), batch_size)]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        
        for future in as_completed(futures):
            batch_results = future.result()
            results.extend(batch_results)
    
    # Sort by frame_index to maintain order
    results.sort(key=lambda x: x.frame_index)
    
    return results


def estimate_poses_3d(poses_2d: Iterable[Pose2DResult]) -> list[Pose3DResult]:
    """
    Optional VideoPose3D lifting step.

    When the VideoPose3D dependency is not present, this function returns an
    empty list and downstream consumers should handle the absence gracefully.
    """
    if TemporalModel is None:
        return []

    # Placeholder: instantiate VideoPose3D model and perform inference.
    model = TemporalModel(
        num_joints_in=33,
        in_features=2,
        num_joints_out=33,
        filter_widths=[3, 3, 3],
    )
    model.eval()

    poses_3d: list[Pose3DResult] = []
    for pose in poses_2d:
        # In a real implementation, stack a temporal window of keypoints.
        input_2d = pose.keypoints[:, :2][None, ...]  # Shape (1, 33, 2)
        with np.errstate(all="ignore"):
            predicted = model(input_2d)  # type: ignore[misc]
        keypoints3d = np.zeros((33, 3), dtype=np.float32)
        poses_3d.append(Pose3DResult(frame_index=pose.frame_index, keypoints=keypoints3d))

    return poses_3d

