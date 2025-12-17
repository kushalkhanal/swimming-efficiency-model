"""
Pose estimation utilities built on MediaPipe and optional VideoPose3D.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

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


def extract_poses_2d(frames: Iterable[DetectedFrame]) -> list[Pose2DResult]:
    """
    Run MediaPipe Pose on each frame and return 33-keypoint landmarks.
    """
    pose_solution = _build_mediapipe_solution()
    results: list[Pose2DResult] = []

    with pose_solution as pose:
        for detected in frames:
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

            results.append(Pose2DResult(frame_index=detected.frame_index, keypoints=keypoints))

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

