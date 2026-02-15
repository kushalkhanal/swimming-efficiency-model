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
    # New advanced metrics
    entry_exit_metrics: dict[str, float]
    streamline_scores: list[float]
    avg_streamline: float
    max_streamline: float
    propulsion_efficiency: float
    slipping_percentage: float
    effective_stroke_percentage: float


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
            "entry_exit_metrics": {},
            "streamline_scores": [],
            "avg_streamline": 0.0,
            "max_streamline": 0.0,
            "propulsion_efficiency": 0.0,
            "slipping_percentage": 0.0,
            "effective_stroke_percentage": 0.0,
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
    
    # Calculate new advanced metrics
    # Entry/Exit Mechanics
    entry_exit = analyze_entry_exit_mechanics(keypoints_data, fps)
    
    # Streamline Score
    streamline_metrics = calculate_streamline_score(keypoints_data)
    
    # Propulsion Efficiency
    propulsion_metrics = analyze_propulsion_efficiency(
        keypoints_data,
        {"hand_left": hand_left_velocities, "hand_right": hand_right_velocities},
        fps
    )
    
    # Add new metrics to payload
    metrics["entry_exit_metrics"] = entry_exit
    metrics["streamline_scores"] = streamline_metrics["streamline_scores"]
    metrics["avg_streamline"] = streamline_metrics["avg_streamline"]
    metrics["max_streamline"] = streamline_metrics["max_streamline"]
    metrics["propulsion_efficiency"] = propulsion_metrics["propulsion_efficiency"]
    metrics["slipping_percentage"] = propulsion_metrics["slipping_percentage"]
    metrics["effective_stroke_percentage"] = propulsion_metrics["effective_stroke_percentage"]
    
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


def analyze_entry_exit_mechanics(keypoints_data: list[dict], fps: float = 30.0) -> dict[str, float]:
    """
    Analyze hand entry and exit mechanics to detect technique quality.
    
    Entry analysis:
    - Entry angle (angle of hand relative to water surface)
    - Entry position (overreach detection)
    - Entry smoothness
    
    Exit analysis:
    - Exit timing (relative to hip position)
    - Exit position quality
    """
    entry_scores = []
    exit_scores = []
    entry_events = 0
    exit_events = 0
    
    # Track wrist velocities to detect entry/exit phases
    for i in range(1, len(keypoints_data)):
        kp_prev = keypoints_data[i-1]
        kp_curr = keypoints_data[i]
        
        # Analyze left hand
        if kp_prev["left_wrist"] is not None and kp_curr["left_wrist"] is not None:
            wrist_vel_y = kp_curr["left_wrist"][1] - kp_prev["left_wrist"][1]
            
            # Entry detection: wrist moving down (y increasing, positive direction is down)
            if wrist_vel_y > 0.5:  # Moving downward threshold
                entry_events += 1
                if (kp_curr["left_shoulder"] is not None and 
                    kp_curr["left_elbow"] is not None):
                    # Calculate entry angle
                    entry_angle = calculate_angle(
                        kp_curr["left_shoulder"],
                        kp_curr["left_elbow"],
                        kp_curr["left_wrist"]
                    )
                    # Good entry: 40-60 degree angle
                    if 40 <= entry_angle <= 60:
                        entry_scores.append(90)
                    elif 35 <= entry_angle <= 70:
                        entry_scores.append(70)
                    else:
                        entry_scores.append(50)
            
            # Exit detection: wrist moving up (y decreasing)
            elif wrist_vel_y < -0.5:  # Moving upward threshold
                exit_events += 1
                if kp_curr["left_hip"] is not None:
                    # Check exit position relative to hip
                    exit_position_x = kp_curr["left_wrist"][0] - kp_curr["left_hip"][0]
                    # Good exit: near hip (not too early, not too late)
                    if abs(exit_position_x) < 0.1:
                        exit_scores.append(90)
                    elif abs(exit_position_x) < 0.2:
                        exit_scores.append(70)
                    else:
                        exit_scores.append(50)
        
        # Analyze right hand (same logic)
        if kp_prev["right_wrist"] is not None and kp_curr["right_wrist"] is not None:
            wrist_vel_y = kp_curr["right_wrist"][1] - kp_prev["right_wrist"][1]
            
            if wrist_vel_y > 0.5:
                entry_events += 1
                if (kp_curr["right_shoulder"] is not None and 
                    kp_curr["right_elbow"] is not None):
                    entry_angle = calculate_angle(
                        kp_curr["right_shoulder"],
                        kp_curr["right_elbow"],
                        kp_curr["right_wrist"]
                    )
                    if 40 <= entry_angle <= 60:
                        entry_scores.append(90)
                    elif 35 <= entry_angle <= 70:
                        entry_scores.append(70)
                    else:
                        entry_scores.append(50)
            
            elif wrist_vel_y < -0.5:
                exit_events += 1
                if kp_curr["right_hip"] is not None:
                    exit_position_x = kp_curr["right_wrist"][0] - kp_curr["right_hip"][0]
                    if abs(exit_position_x) < 0.1:
                        exit_scores.append(90)
                    elif abs(exit_position_x) < 0.2:
                        exit_scores.append(70)
                    else:
                        exit_scores.append(50)
    
    return {
        "avg_entry_score": float(np.mean(entry_scores)) if entry_scores else 0.0,
        "avg_exit_score": float(np.mean(exit_scores)) if exit_scores else 0.0,
        "entry_events": float(entry_events),
        "exit_events": float(exit_events),
    }


def calculate_streamline_score(keypoints_data: list[dict]) -> dict[str, any]:
    """
    Calculate streamline score (0-100) based on body position efficiency.
    
    Measures:
    - Head-spine-hip alignment
    - Hip height (body flatness in water)
    - Leg alignment and position
    """
    streamline_scores = []
    
    for kp in keypoints_data:
        penalties = 0.0
        max_penalties = 3.0  # Three components
        
        # Component 1: Head-spine alignment
        if (kp["nose"] is not None and 
            kp["left_shoulder"] is not None and 
            kp["right_shoulder"] is not None and
            kp["left_hip"] is not None and 
            kp["right_hip"] is not None):
            
            shoulder_mid = (kp["left_shoulder"] + kp["right_shoulder"]) / 2
            hip_mid = (kp["left_hip"] + kp["right_hip"]) / 2
            
            # Calculate head elevation relative to body line
            # Ideal: head in line with spine
            head_y = kp["nose"][1]
            body_line_y = shoulder_mid[1]
            head_deviation = abs(head_y - body_line_y)
            
            # Normalize penalty (0 = perfect, 1 = very bad)
            head_penalty = min(head_deviation * 2, 1.0)
            penalties += head_penalty
            
            # Component 2: Hip drop (body flatness)
            # Ideal: hips at same level as shoulders
            hip_drop = abs(hip_mid[1] - shoulder_mid[1])
            hip_penalty = min(hip_drop * 1.5, 1.0)
            penalties += hip_penalty
        else:
            penalties += 2.0  # Can't calculate, assume poor
        
        # Component 3: Leg alignment
        if (kp["left_knee"] is not None and 
            kp["right_knee"] is not None and
            kp["left_ankle"] is not None and 
            kp["right_ankle"] is not None):
            
            # Measure leg spread (legs should be close together)
            knee_spread = np.linalg.norm(kp["left_knee"] - kp["right_knee"])
            ankle_spread = np.linalg.norm(kp["left_ankle"] - kp["right_ankle"])
            avg_spread = (knee_spread + ankle_spread) / 2
            
            # Normalize penalty
            leg_penalty = min(avg_spread * 3, 1.0)
            penalties += leg_penalty
        else:
            penalties += 1.0
        
        # Calculate score (100 = perfect streamline)
        score = 100 * (1 - penalties / max_penalties)
        streamline_scores.append(max(0, min(100, score)))  # Clamp to 0-100
    
    return {
        "streamline_scores": streamline_scores,
        "avg_streamline": float(np.mean(streamline_scores)) if streamline_scores else 0.0,
        "max_streamline": float(np.max(streamline_scores)) if streamline_scores else 0.0,
        "streamline_consistency": float(1 - np.std(streamline_scores) / (np.mean(streamline_scores) + 1e-8)) if streamline_scores else 0.0,
    }


def analyze_propulsion_efficiency(
    keypoints_data: list[dict],
    hand_velocities: dict[str, list[float]],
    fps: float = 30.0
) -> dict[str, float]:
    """
    Analyze propulsion efficiency to detect effective pulling vs slipping.
    
    Slipping: High hand velocity but no forward body movement
    Effective: Hand velocity translates to body acceleration
    """
    # Calculate body center velocity as proxy for forward movement
    body_centers = []
    for kp in keypoints_data:
        if (kp["left_shoulder"] is not None and 
            kp["right_shoulder"] is not None and
            kp["left_hip"] is not None and 
            kp["right_hip"] is not None):
            shoulder_mid = (kp["left_shoulder"] + kp["right_shoulder"]) / 2
            hip_mid = (kp["left_hip"] + kp["right_hip"]) / 2
            body_center = (shoulder_mid + hip_mid) / 2
            body_centers.append((body_center[0], body_center[1]))
        else:
            body_centers.append((0.0, 0.0))
    
    # Calculate body velocity
    body_velocities = calculate_velocity(body_centers, fps)
    
    # Analyze propulsion efficiency
    propulsion_events = []
    slipping_frames = 0
    effective_frames = 0
    total_frames = len(keypoints_data)
    
    hand_left_vel = hand_velocities.get("hand_left", [])
    hand_right_vel = hand_velocities.get("hand_right", [])
    
    for i in range(1, min(len(hand_left_vel), len(hand_right_vel), len(body_velocities))):
        avg_hand_vel = (hand_left_vel[i] + hand_right_vel[i]) / 2
        body_vel = body_velocities[i]
        body_accel = body_velocities[i] - body_velocities[i-1] if i > 0 else 0
        
        # Define thresholds
        hand_vel_threshold = 1.0  # Significant hand movement
        body_accel_threshold = 0.05  # Body actually accelerating
        
        if avg_hand_vel > hand_vel_threshold:
            # Hand is moving - is it effective?
            if body_accel > body_accel_threshold:
                # Effective propulsion
                effective_frames += 1
                efficiency = min(body_accel / avg_hand_vel, 1.0)  # How much hand movement→body movement
                propulsion_events.append(efficiency * 100)
            elif body_accel < -body_accel_threshold:
                # Actually decelerating - slipping
                slipping_frames += 1
            # else: neutral, not counted either way
    
    return {
        "propulsion_efficiency": float(np.mean(propulsion_events)) if propulsion_events else 0.0,
        "slipping_percentage": float((slipping_frames / total_frames) * 100) if total_frames > 0 else 0.0,
        "effective_stroke_percentage": float((effective_frames / total_frames) * 100) if total_frames > 0 else 0.0,
    }



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
    if avg_velocity > 2.0:
        key_takeaways.append(f"Strong average velocity of {avg_velocity:.2f} m/s.")
    else:
        key_takeaways.append(f"Average velocity is {avg_velocity:.2f} m/s.")
        recommendations.append("Work on pull power and kick propulsion to increase forward speed.")
    
    if avg_velocity > 0:
        velocity_consistency = max_velocity / avg_velocity if avg_velocity > 0 else 1.0
        if velocity_consistency > 2.5:
            recommendations.append("High velocity variation detected - work on consistent power application.")
        elif velocity_consistency < 1.3:
            recommendations.append("Good velocity consistency throughout the stroke.")
    
    # Streamline Score analysis
    avg_streamline = metrics.get("avg_streamline", 0)
    if avg_streamline >= 80:
        key_takeaways.append(f"✅ Excellent streamline position ({avg_streamline:.1f}/100).")
    elif avg_streamline >= 65:
        key_takeaways.append(f"Good body position with streamline score of {avg_streamline:.1f}/100.")
        recommendations.append("Focus on keeping hips high and head neutral to improve streamline.")
    else:
        key_takeaways.append(f"⚠️ Streamline needs improvement ({avg_streamline:.1f}/100).")
        recommendations.append("Work on core stability and body position drills. Keep head down and hips up.")
    
    # Propulsion Efficiency analysis
    prop_efficiency = metrics.get("propulsion_efficiency", 0)
    slipping_pct = metrics.get("slipping_percentage", 0)
    if slipping_pct > 15:
        key_takeaways.append(f"⚠️ {slipping_pct:.1f}% of strokes show hand slipping.")
        recommendations.append("Focus on high elbow catch and early vertical forearm to 'grip' the water better.")
    elif slipping_pct > 8:
        key_takeaways.append(f"Moderate hand slipping detected ({slipping_pct:.1f}%).")
        recommendations.append("Work on catch mechanics to improve water connection.")
    else:
        key_takeaways.append("✅ Excellent propulsion with minimal hand slipping.")
    
    # Entry/Exit Mechanics
    entry_exit = metrics.get("entry_exit_metrics", {})
    avg_entry = entry_exit.get("avg_entry_score", 0)
    avg_exit = entry_exit.get("avg_exit_score", 0)
    if avg_entry > 0:
        if avg_entry >= 80:
            key_takeaways.append(f"✅ Hand entry mechanics are strong ({avg_entry:.1f}/100).")
        elif avg_entry >= 60:
            key_takeaways.append(f"Hand entry is decent ({avg_entry:.1f}/100).")
            recommendations.append("Focus on entering at 45° angle, fingertips first, in front of shoulder.")
        else:
            key_takeaways.append(f"⚠️ Hand entry needs work ({avg_entry:.1f}/100).")
            recommendations.append("Practice fingertip entry drills. Avoid overreaching or slapping water.")
    
    if avg_exit > 0:
        if avg_exit < 65:
            recommendations.append("Work on finishing stroke past hip for complete propulsion.")
    
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

