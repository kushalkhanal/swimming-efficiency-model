"""
Helper functions for calculating biomechanical metrics for a single frame.
"""

from __future__ import annotations

import numpy as np
from math import atan2, degrees, sqrt


def calculate_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate angle at p2 formed by vectors p1->p2 and p3->p2."""
    v1 = p1 - p2
    v2 = p3 - p2
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return degrees(np.arccos(cos_angle))


def calculate_joint_angles_single_frame(keypoints: np.ndarray) -> dict[str, float]:
    """
    Calculate joint angles for a single frame of pose keypoints.
    
    Args:
        keypoints: np.ndarray of shape (33, 4) containing [x, y, z, visibility]
    
    Returns:
        Dictionary with joint angle values
    """
    # MediaPipe Pose landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    
    angles = {}
    
    # Extract keypoints (only if visible)
    def get_point(idx: int) -> np.ndarray | None:
        if keypoints[idx, 3] > 0.5:  # Check visibility
            return keypoints[idx, :2]
        return None
    
    # Left elbow angle (shoulder-elbow-wrist)
    ls = get_point(LEFT_SHOULDER)
    le = get_point(LEFT_ELBOW)
    lw = get_point(LEFT_WRIST)
    if ls is not None and le is not None and lw is not None:
        angles['left_elbow'] = calculate_angle(ls, le, lw)
    
    # Right elbow angle
    rs = get_point(RIGHT_SHOULDER)
    re = get_point(RIGHT_ELBOW)
    rw = get_point(RIGHT_WRIST)
    if rs is not None and re is not None and rw is not None:
        angles['right_elbow'] = calculate_angle(rs, re, rw)
    
    # Left shoulder angle (hip-shoulder-elbow)
    lh = get_point(LEFT_HIP)
    if lh is not None and ls is not None and le is not None:
        angles['left_shoulder'] = calculate_angle(lh, ls, le)
    
    # Right shoulder angle
    rh = get_point(RIGHT_HIP)
    if rh is not None and rs is not None and re is not None:
        angles['right_shoulder'] = calculate_angle(rh, rs, re)
    
    # Left knee angle (hip-knee-ankle)
    lk = get_point(LEFT_KNEE)
    la = get_point(LEFT_ANKLE)
    if lh is not None and lk is not None and la is not None:
        angles['left_knee'] = calculate_angle(lh, lk, la)
    
    # Right knee angle
    rk = get_point(RIGHT_KNEE)
    ra = get_point(RIGHT_ANKLE)
    if rh is not None and rk is not None and ra is not None:
        angles['right_knee'] = calculate_angle(rh, rk, ra)
    
    return angles


def rate_joint_angle(angle: float, joint_name: str) -> str:
    """
    Rate a joint angle based on biomechanical standards.
    
    Returns: 'excellent', 'good', 'needs_work', or 'poor'
    """
    joint_lower = joint_name.lower()
    
    if 'elbow' in joint_lower:
        # Optimal elbow catch angle: 90-120 degrees
        if 90 <= angle <= 120:
            return 'excellent'
        elif 70 <= angle < 90 or 120 < angle <= 140:
            return 'good'
        elif 60 <= angle < 70 or 140 < angle <= 160:
            return 'needs_work'
        else:
            return 'poor'
    
    elif 'shoulder' in joint_lower:
        # Optimal shoulder angle during pull: 80-110 degrees
        if 80 <= angle <= 110:
            return 'excellent'
        elif 65 <= angle < 80 or 110 < angle <= 130:
            return 'good'
        elif 50 <= angle < 65 or 130 < angle <= 150:
            return 'needs_work'
        else:
            return 'poor'
    
    elif 'knee' in joint_lower:
        # Optimal knee flexion during kick: 120-160 degrees
        if 120 <= angle <= 160:
            return 'excellent'
        elif 100 <= angle < 120 or 160 < angle <= 175:
            return 'good'
        elif 80 <= angle < 100:
            return 'needs_work'
        else:
            return 'poor'
    
    # Default rating
    return 'good'
