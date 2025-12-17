"""
Biomechanical analytics calculations.

This module computes comprehensive biomechanical metrics from pose keypoints
including joint angles, velocities, body roll, symmetry, and stroke phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, sqrt
from typing import Iterable, TypedDict

import numpy as np
from scipy import signal

from .pose_estimation import Pose2DResult, Pose3DResult

# MediaPipe Pose landmark indices
# See: https://google.github.io/mediapipe/solutions/pose.html
NOSE = 0
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


class MetricsPayload(TypedDict):
    frame_indices: list[int]
    joint_angles: dict[str, list[float]]
    body_roll: list[float]
    symmetry_index: float
    stroke_rate: float
    stroke_length: float
    velocities: dict[str, list[float]]
    kick_timing: list[float]
    breathing_events: list[int]
    avg_velocity: float
    max_velocity: float
    body_alignment: list[float]


@dataclass(slots=True)
class StrokePhase:
    phase_name: str
    frame_indices: list[int]


def calculate_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate angle at p2 formed by vectors p1->p2 and p3->p2."""
    v1 = p1 - p2
    v2 = p3 - p2
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return degrees(np.arccos(cos_angle))


def calculate_velocity(positions: list[tuple[float, float]], fps: float = 30.0) -> list[float]:
    """Calculate velocities from position sequences."""
    if len(positions) < 2:
        return [0.0] * len(positions)
    
    velocities = [0.0]
    for i in range(1, len(positions)):
        dx = positions[i][0] - positions[i-1][0]
        dy = positions[i][1] - positions[i-1][1]
        dist = sqrt(dx*dx + dy*dy)
        velocities.append(dist * fps)
    return velocities


def detect_stroke_cycle(hand_positions: list[float], min_cycle_frames: int = 30) -> list[int]:
    """Detect stroke cycles using peak detection on hand positions."""
    if len(hand_positions) < min_cycle_frames:
        return []
    
    # Normalize positions
    positions = np.array(hand_positions)
    if np.std(positions) < 0.01:
        return []
    
    # Find peaks (stroke cycles)
    peaks, _ = signal.find_peaks(positions, distance=min_cycle_frames)
    return [int(p) for p in peaks]


def compute_biomechanics_metrics(
    poses2d: Iterable[Pose2DResult],
    poses3d: Iterable[Pose3DResult] | None = None,
    fps: float = 30.0,
) -> MetricsPayload:
    """
    Compute comprehensive biomechanical metrics from 2D/3D pose sequences.
    
    Calculates:
    - Joint angles (elbows, shoulders, knees)
    - Body roll (shoulder rotation)
    - Hand velocities
    - Stroke rate and length
    - Symmetry index
    - Kick timing
    - Breathing events
    """
    poses2d_list = list(poses2d)
    if not poses2d_list:
        # Return empty metrics if no poses
        return {
            "frame_indices": [],
            "joint_angles": {},
            "body_roll": [],
            "symmetry_index": 0.0,
            "stroke_rate": 0.0,
            "stroke_length": 0.0,
            "velocities": {},
            "kick_timing": [],
            "breathing_events": [],
            "avg_velocity": 0.0,
            "max_velocity": 0.0,
            "body_alignment": [],
        }
    
    frame_numbers = [pose.frame_index for pose in poses2d_list]
    n_frames = len(frame_numbers)
    
    # Extract keypoints for each frame
    keypoints_data = []
    for pose in poses2d_list:
        kp = pose.keypoints
        # Only use visible keypoints (visibility > 0.5)
        visible = kp[:, 3] > 0.5
        keypoints_data.append({
            "nose": kp[NOSE, :2] if visible[NOSE] else None,
            "left_shoulder": kp[LEFT_SHOULDER, :2] if visible[LEFT_SHOULDER] else None,
            "right_shoulder": kp[RIGHT_SHOULDER, :2] if visible[RIGHT_SHOULDER] else None,
            "left_elbow": kp[LEFT_ELBOW, :2] if visible[LEFT_ELBOW] else None,
            "right_elbow": kp[RIGHT_ELBOW, :2] if visible[RIGHT_ELBOW] else None,
            "left_wrist": kp[LEFT_WRIST, :2] if visible[LEFT_WRIST] else None,
            "right_wrist": kp[RIGHT_WRIST, :2] if visible[RIGHT_WRIST] else None,
            "left_hip": kp[LEFT_HIP, :2] if visible[LEFT_HIP] else None,
            "right_hip": kp[RIGHT_HIP, :2] if visible[RIGHT_HIP] else None,
            "left_knee": kp[LEFT_KNEE, :2] if visible[LEFT_KNEE] else None,
            "right_knee": kp[RIGHT_KNEE, :2] if visible[RIGHT_KNEE] else None,
            "left_ankle": kp[LEFT_ANKLE, :2] if visible[LEFT_ANKLE] else None,
            "right_ankle": kp[RIGHT_ANKLE, :2] if visible[RIGHT_ANKLE] else None,
        })
    
    # Compute joint angles
    elbow_left_angles = []
    elbow_right_angles = []
    shoulder_left_angles = []
    shoulder_right_angles = []
    knee_left_angles = []
    knee_right_angles = []
    
    for i, kp in enumerate(keypoints_data):
        # Left elbow angle (shoulder-elbow-wrist)
        if kp["left_shoulder"] is not None and kp["left_elbow"] is not None and kp["left_wrist"] is not None:
            angle = calculate_angle(kp["left_shoulder"], kp["left_elbow"], kp["left_wrist"])
            elbow_left_angles.append(angle)
        else:
            elbow_left_angles.append(0.0)
        
        # Right elbow angle
        if kp["right_shoulder"] is not None and kp["right_elbow"] is not None and kp["right_wrist"] is not None:
            angle = calculate_angle(kp["right_shoulder"], kp["right_elbow"], kp["right_wrist"])
            elbow_right_angles.append(angle)
        else:
            elbow_right_angles.append(0.0)
        
        # Left shoulder angle (hip-shoulder-elbow)
        if kp["left_hip"] is not None and kp["left_shoulder"] is not None and kp["left_elbow"] is not None:
            angle = calculate_angle(kp["left_hip"], kp["left_shoulder"], kp["left_elbow"])
            shoulder_left_angles.append(angle)
        else:
            shoulder_left_angles.append(0.0)
        
        # Right shoulder angle
        if kp["right_hip"] is not None and kp["right_shoulder"] is not None and kp["right_elbow"] is not None:
            angle = calculate_angle(kp["right_hip"], kp["right_shoulder"], kp["right_elbow"])
            shoulder_right_angles.append(angle)
        else:
            shoulder_right_angles.append(0.0)
        
        # Left knee angle (hip-knee-ankle)
        if kp["left_hip"] is not None and kp["left_knee"] is not None and kp["left_ankle"] is not None:
            angle = calculate_angle(kp["left_hip"], kp["left_knee"], kp["left_ankle"])
            knee_left_angles.append(angle)
        else:
            knee_left_angles.append(0.0)
        
        # Right knee angle
        if kp["right_hip"] is not None and kp["right_knee"] is not None and kp["right_ankle"] is not None:
            angle = calculate_angle(kp["right_hip"], kp["right_knee"], kp["right_ankle"])
            knee_right_angles.append(angle)
        else:
            knee_right_angles.append(0.0)
    
    # Compute body roll (angle between shoulders and horizontal)
    body_roll = []
    for kp in keypoints_data:
        if kp["left_shoulder"] is not None and kp["right_shoulder"] is not None:
            dx = kp["right_shoulder"][0] - kp["left_shoulder"][0]
            dy = kp["right_shoulder"][1] - kp["left_shoulder"][1]
            roll = degrees(atan2(dy, dx))
            body_roll.append(roll)
        else:
            body_roll.append(0.0)
    
    # Compute hand velocities
    left_wrist_positions = [
        (kp["left_wrist"][0], kp["left_wrist"][1]) 
        if kp["left_wrist"] is not None else (0.0, 0.0)
        for kp in keypoints_data
    ]
    right_wrist_positions = [
        (kp["right_wrist"][0], kp["right_wrist"][1])
        if kp["right_wrist"] is not None else (0.0, 0.0)
        for kp in keypoints_data
    ]
    
    hand_left_velocities = calculate_velocity(left_wrist_positions, fps)
    hand_right_velocities = calculate_velocity(right_wrist_positions, fps)
    
    # Detect stroke cycles from hand Y positions (upward/downward motion)
    left_hand_y = [pos[1] if pos[0] > 0 else 0.0 for pos in left_wrist_positions]
    right_hand_y = [pos[1] if pos[0] > 0 else 0.0 for pos in right_wrist_positions]
    
    # Combine hand positions for cycle detection
    avg_hand_y = [(l + r) / 2.0 for l, r in zip(left_hand_y, right_hand_y)]
    stroke_cycles = detect_stroke_cycle(avg_hand_y)
    
    # Calculate stroke rate (strokes per minute)
    if len(stroke_cycles) > 1:
        total_time = n_frames / fps  # seconds
        n_strokes = len(stroke_cycles) - 1
        stroke_rate = (n_strokes / total_time) * 60.0 if total_time > 0 else 0.0
        # Estimate stroke length (arbitrary units, would need calibration)
        stroke_length = np.mean([avg_hand_y[stroke_cycles[i+1]] - avg_hand_y[stroke_cycles[i]]
                                 for i in range(len(stroke_cycles)-1)]) if len(stroke_cycles) > 1 else 0.0
    else:
        stroke_rate = 0.0
        stroke_length = 0.0
    
    # Calculate symmetry index (correlation between left and right angles)
    if len(elbow_left_angles) > 10 and len(elbow_right_angles) > 10:
        # Use correlation as symmetry measure (1.0 = perfect symmetry)
        correlation = np.corrcoef(elbow_left_angles, elbow_right_angles)[0, 1]
        symmetry_index = max(0.0, min(1.0, (correlation + 1) / 2.0))  # Normalize to [0, 1]
    else:
        symmetry_index = 0.5
    
    # Detect breathing events (when head rises)
    breathing_events = []
    if keypoints_data and keypoints_data[0]["nose"] is not None:
        nose_y = [kp["nose"][1] if kp["nose"] is not None else 0.0 for kp in keypoints_data]
        if len(nose_y) > 20:
            # Find local minima (head highest = breathing)
            peaks, _ = signal.find_peaks([-y for y in nose_y], distance=30)
            breathing_events = [int(p) for p in peaks]
    
    # Kick timing (ankle velocities)
    left_ankle_positions = [
        (kp["left_ankle"][0], kp["left_ankle"][1])
        if kp["left_ankle"] is not None else (0.0, 0.0)
        for kp in keypoints_data
    ]
    kick_timing = calculate_velocity(left_ankle_positions, fps)
    
    # Body alignment (angle from shoulders to hips)
    body_alignment = []
    for kp in keypoints_data:
        if (kp["left_shoulder"] is not None and kp["right_shoulder"] is not None and
            kp["left_hip"] is not None and kp["right_hip"] is not None):
            shoulder_mid = (kp["left_shoulder"] + kp["right_shoulder"]) / 2
            hip_mid = (kp["left_hip"] + kp["right_hip"]) / 2
            dx = hip_mid[0] - shoulder_mid[0]
            dy = hip_mid[1] - shoulder_mid[1]
            alignment = degrees(atan2(dy, dx))
            body_alignment.append(alignment)
        else:
            body_alignment.append(0.0)
    
    # Average and max velocities
    all_velocities = hand_left_velocities + hand_right_velocities
    avg_velocity = np.mean(all_velocities) if all_velocities else 0.0
    max_velocity = np.max(all_velocities) if all_velocities else 0.0
    
    metrics: MetricsPayload = {
        "frame_indices": frame_numbers,
        "joint_angles": {
            "elbow_left": [float(a) for a in elbow_left_angles],
            "elbow_right": [float(a) for a in elbow_right_angles],
            "shoulder_left": [float(a) for a in shoulder_left_angles],
            "shoulder_right": [float(a) for a in shoulder_right_angles],
            "knee_left": [float(a) for a in knee_left_angles],
            "knee_right": [float(a) for a in knee_right_angles],
        },
        "body_roll": [float(r) for r in body_roll],
        "symmetry_index": float(symmetry_index),
        "stroke_rate": float(stroke_rate),
        "stroke_length": float(stroke_length),
        "velocities": {
            "hand_left": [float(v) for v in hand_left_velocities],
            "hand_right": [float(v) for v in hand_right_velocities],
        },
        "kick_timing": [float(k) for k in kick_timing],
        "breathing_events": breathing_events,
        "avg_velocity": float(avg_velocity),
        "max_velocity": float(max_velocity),
        "body_alignment": [float(a) for a in body_alignment],
    }
    
    return metrics


def segment_stroke_phases(
    poses2d: Iterable[Pose2DResult], metrics: MetricsPayload
) -> list[StrokePhase]:
    """
    Rule-based stroke phase segmentation using hand velocities and positions.
    
    Detects phases:
    - Catch: Hand entry into water
    - Pull: Propulsive phase
    - Push: Final propulsive phase
    - Recovery: Hand out of water
    """
    poses2d_list = list(poses2d)
    if not poses2d_list:
        return []
    
    frame_numbers = metrics["frame_indices"]
    if not frame_numbers:
        return []
    
    # Use hand velocities to detect phases
    hand_left_vel = metrics["velocities"]["hand_left"]
    hand_right_vel = metrics["velocities"]["hand_right"]
    avg_vel = [(l + r) / 2.0 for l, r in zip(hand_left_vel, hand_right_vel)]
    
    if len(avg_vel) < 10:
        # Not enough data, return simple segmentation
        mid_point = len(frame_numbers) // 2
        return [
            StrokePhase(phase_name="catch", frame_indices=frame_numbers[:mid_point]),
            StrokePhase(phase_name="pull", frame_indices=frame_numbers[mid_point:]),
        ]
    
    # Find velocity peaks (max speed = pull/push phase)
    avg_vel_array = np.array(avg_vel)
    if np.max(avg_vel_array) - np.min(avg_vel_array) < 0.1:
        # Low variation, return simple segmentation
        mid_point = len(frame_numbers) // 2
        return [
            StrokePhase(phase_name="catch", frame_indices=frame_numbers[:mid_point]),
            StrokePhase(phase_name="pull", frame_indices=frame_numbers[mid_point:]),
        ]
    
    # Normalize velocities
    vel_normalized = (avg_vel_array - np.min(avg_vel_array)) / (np.max(avg_vel_array) - np.min(avg_vel_array) + 1e-8)
    
    # Detect phases based on velocity thresholds
    phases = []
    catch_threshold = 0.2
    pull_threshold = 0.6
    recovery_threshold = 0.3
    
    catch_frames = []
    pull_frames = []
    push_frames = []
    recovery_frames = []
    
    for i, vel in enumerate(vel_normalized):
        if vel < catch_threshold:
            catch_frames.append(frame_numbers[i])
        elif vel < pull_threshold:
            pull_frames.append(frame_numbers[i])
        elif vel > pull_threshold:
            push_frames.append(frame_numbers[i])
        else:
            recovery_frames.append(frame_numbers[i])
    
    if catch_frames:
        phases.append(StrokePhase(phase_name="catch", frame_indices=catch_frames))
    if pull_frames:
        phases.append(StrokePhase(phase_name="pull", frame_indices=pull_frames))
    if push_frames:
        phases.append(StrokePhase(phase_name="push", frame_indices=push_frames))
    if recovery_frames:
        phases.append(StrokePhase(phase_name="recovery", frame_indices=recovery_frames))
    
    # If no phases detected, return simple split
    if not phases:
        mid_point = len(frame_numbers) // 2
        return [
            StrokePhase(phase_name="catch", frame_indices=frame_numbers[:mid_point]),
            StrokePhase(phase_name="pull", frame_indices=frame_numbers[mid_point:]),
        ]
    
    return phases


def generate_narrative_feedback(
    metrics: MetricsPayload, stroke_phases: Iterable[StrokePhase]
) -> dict[str, str]:
    """
    Construct comprehensive narrative feedback using metric thresholds and biomechanical insights.
    """
    symmetry = metrics["symmetry_index"]
    stroke_rate = metrics["stroke_rate"]
    avg_velocity = metrics["avg_velocity"]
    max_velocity = metrics["max_velocity"]
    
    key_takeaways = []
    recommendations = []
    
    # Symmetry analysis
    if symmetry < 0.7:
        key_takeaways.append("⚠️ Significant asymmetry detected between left and right strokes.")
        recommendations.append("Focus on bilateral balance exercises and stroke symmetry drills.")
    elif symmetry < 0.85:
        key_takeaways.append("Moderate asymmetry observed in stroke mechanics.")
        recommendations.append("Work on evening out left/right pull timing and power application.")
    else:
        key_takeaways.append("✅ Excellent left/right balance throughout the stroke cycle.")
    
    # Stroke rate analysis
    if stroke_rate < 20:
        key_takeaways.append("Stroke rate is quite low.")
        recommendations.append("Consider increasing stroke frequency for race-pace efficiency.")
    elif stroke_rate < 26:
        key_takeaways.append("Stroke rate is moderate.")
        recommendations.append("Aim for 28-32 SPM for competitive freestyle swimming.")
    elif stroke_rate < 35:
        key_takeaways.append("✅ Stroke rate is within competitive range.")
    else:
        key_takeaways.append("Stroke rate is high - ensure maintaining technique at this pace.")
        recommendations.append("Focus on maintaining power per stroke at higher rates.")
    
    # Velocity analysis
    if avg_velocity > 0:
        velocity_consistency = max_velocity / avg_velocity if avg_velocity > 0 else 1.0
        if velocity_consistency > 2.5:
            recommendations.append("High velocity variation detected - work on consistent power application.")
        elif velocity_consistency < 1.3:
            recommendations.append("Good velocity consistency throughout the stroke.")
    
    # Body roll analysis
    body_roll = metrics.get("body_roll", [])
    if body_roll:
        avg_roll = np.mean([abs(r) for r in body_roll])
        if avg_roll < 15:
            recommendations.append("Increase body rotation (roll) for improved stroke efficiency and power.")
        elif avg_roll > 45:
            recommendations.append("Body roll is excessive - reduce rotation to maintain streamline.")
        else:
            recommendations.append("✅ Body rotation is within optimal range.")
    
    # Joint angles analysis
    joint_angles = metrics.get("joint_angles", {})
    if joint_angles:
        elbow_left = joint_angles.get("elbow_left", [])
        elbow_right = joint_angles.get("elbow_right", [])
        if elbow_left and elbow_right:
            avg_left = np.mean([a for a in elbow_left if a > 0])
            avg_right = np.mean([a for a in elbow_right if a > 0])
            
            if avg_left < 90 or avg_right < 90:
                recommendations.append("Elbow angles are quite low - work on high elbow catch position.")
            elif avg_left > 160 or avg_right > 160:
                recommendations.append("Elbow extension is very high - ensure proper pull-through technique.")
    
    # Phase breakdown
    phase_breakdown = {}
    total_frames = len(metrics["frame_indices"])
    for phase in stroke_phases:
        phase_frames = len(phase.frame_indices)
        percentage = (phase_frames / total_frames * 100) if total_frames > 0 else 0
        phase_breakdown[phase.phase_name] = {
            "frames": phase_frames,
            "percentage": f"{percentage:.1f}%"
        }
    
    # Create summary
    summary = " ".join(key_takeaways)
    if recommendations:
        summary += "\n\nRecommendations:\n" + "\n".join(f"• {r}" for r in recommendations)
    
    return {
        "summary": summary,
        "phase_breakdown": phase_breakdown,
        "key_metrics": {
            "symmetry_index": f"{symmetry:.2f}",
            "stroke_rate": f"{stroke_rate:.1f} SPM",
            "avg_velocity": f"{avg_velocity:.2f}",
            "max_velocity": f"{max_velocity:.2f}",
        }
    }

