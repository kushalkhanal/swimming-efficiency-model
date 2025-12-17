"""
Coaching-focused feedback generation with plain-language explanations
and timeline-based analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass
class TimelineSegment:
    """A segment of the video with associated feedback."""
    start_time: float  # seconds
    end_time: float
    start_frame: int
    end_frame: int
    status: str  # "good", "needs_work", "excellent"
    title: str
    feedback: str
    metric_focus: str | None = None


@dataclass
class PlainLanguageMetric:
    """A metric explained in plain language."""
    name: str
    technical_name: str
    value: float
    rating: str  # "excellent", "good", "needs_work", "poor"
    explanation: str
    what_it_means: str
    how_to_improve: str | None = None


def get_rating(value: float, thresholds: dict) -> str:
    """Get rating based on thresholds."""
    if value >= thresholds.get("excellent", float("inf")):
        return "excellent"
    elif value >= thresholds.get("good", float("inf")):
        return "good"
    elif value >= thresholds.get("needs_work", float("inf")):
        return "needs_work"
    return "poor"


def explain_symmetry(value: float) -> PlainLanguageMetric:
    """Explain symmetry index in plain language."""
    if value >= 0.9:
        rating = "excellent"
        explanation = f"Your left and right arms are moving almost identically. Score: {value:.2f}/1.0"
        what_it_means = "This means your stroke is very balanced, which maximizes efficiency and reduces injury risk."
        how_to_improve = None
    elif value >= 0.8:
        rating = "good"
        explanation = f"Your arms are moving fairly evenly. Score: {value:.2f}/1.0"
        what_it_means = "Good balance between sides. Minor differences are normal."
        how_to_improve = "Try single-arm drills to identify which side needs attention."
    elif value >= 0.7:
        rating = "needs_work"
        explanation = f"There's noticeable difference between your left and right strokes. Score: {value:.2f}/1.0"
        what_it_means = "One arm is doing more work than the other, which wastes energy and can cause fatigue."
        how_to_improve = "Focus on catch-up drill and single-arm freestyle to balance your stroke."
    else:
        rating = "poor"
        explanation = f"Significant imbalance detected between left and right. Score: {value:.2f}/1.0"
        what_it_means = "This imbalance is likely slowing you down and could lead to shoulder issues."
        how_to_improve = "Work with a coach on bilateral breathing and symmetry drills. Consider video review from multiple angles."
    
    return PlainLanguageMetric(
        name="Stroke Balance",
        technical_name="Symmetry Index",
        value=value,
        rating=rating,
        explanation=explanation,
        what_it_means=what_it_means,
        how_to_improve=how_to_improve,
    )


def explain_stroke_rate(value: float) -> PlainLanguageMetric:
    """Explain stroke rate in plain language."""
    if value >= 28 and value <= 34:
        rating = "excellent"
        explanation = f"Your stroke rate is {value:.0f} strokes per minute - right in the competitive sweet spot."
        what_it_means = "This is typical for efficient distance freestyle. You're not rushing or dragging."
        how_to_improve = None
    elif value >= 24 and value < 28:
        rating = "good"
        explanation = f"Your stroke rate is {value:.0f} strokes per minute - a comfortable pace."
        what_it_means = "Good for training and longer distances. Could increase for racing."
        how_to_improve = "For race pace, try tempo trainers set to 1.8-2.0 seconds per stroke."
    elif value >= 35:
        rating = "needs_work"
        explanation = f"Your stroke rate is {value:.0f} strokes per minute - quite fast."
        what_it_means = "High turnover can mean shorter strokes. Make sure you're not sacrificing distance per stroke."
        how_to_improve = "Focus on 'front quadrant' swimming - keep one hand extended while the other catches."
    elif value >= 18:
        rating = "needs_work"
        explanation = f"Your stroke rate is {value:.0f} strokes per minute - on the slower side."
        what_it_means = "While long strokes are good, too slow can mean dead spots in your propulsion."
        how_to_improve = "Work on continuous propulsion - as one arm finishes, the other should be catching."
    else:
        rating = "poor"
        explanation = f"Your stroke rate is {value:.0f} strokes per minute - very slow."
        what_it_means = "There are likely long pauses in your stroke where you're gliding without propulsion."
        how_to_improve = "Focus on eliminating dead spots. Try 'catch-up' drill transitioning to normal freestyle."
    
    return PlainLanguageMetric(
        name="Stroke Tempo",
        technical_name="Stroke Rate (SPM)",
        value=value,
        rating=rating,
        explanation=explanation,
        what_it_means=what_it_means,
        how_to_improve=how_to_improve,
    )


def explain_body_roll(avg_roll: float) -> PlainLanguageMetric:
    """Explain body roll in plain language."""
    if avg_roll >= 30 and avg_roll <= 45:
        rating = "excellent"
        explanation = f"Your body rotation averages {avg_roll:.0f}° - textbook form."
        what_it_means = "Good rotation engages your core and back muscles, not just shoulders."
        how_to_improve = None
    elif avg_roll >= 20 and avg_roll < 30:
        rating = "good"
        explanation = f"Your body rotation averages {avg_roll:.0f}° - decent but could be more."
        what_it_means = "You're rotating, but more roll would give you better reach and power."
        how_to_improve = "Try '6-kick switch' drill: 6 kicks on your side, then rotate to the other side."
    elif avg_roll < 20:
        rating = "needs_work"
        explanation = f"Your body rotation averages only {avg_roll:.0f}° - you're swimming too flat."
        what_it_means = "Flat swimming puts all the work on your shoulders and limits your reach."
        how_to_improve = "Practice side-kick drills. Imagine showing your belly button to the side walls as you swim."
    else:
        rating = "needs_work"
        explanation = f"Your body rotation averages {avg_roll:.0f}° - that's excessive."
        what_it_means = "Over-rotation wastes energy and can throw off your timing."
        how_to_improve = "Focus on rotating from your hips, not just shoulders. Keep your head stable."
    
    return PlainLanguageMetric(
        name="Body Rotation",
        technical_name="Body Roll (degrees)",
        value=avg_roll,
        rating=rating,
        explanation=explanation,
        what_it_means=what_it_means,
        how_to_improve=how_to_improve,
    )


def explain_elbow_angle(avg_angle: float, side: str) -> PlainLanguageMetric:
    """Explain elbow angle in plain language."""
    if avg_angle >= 90 and avg_angle <= 120:
        rating = "excellent"
        explanation = f"Your {side} elbow averages {avg_angle:.0f}° during the pull - great high-elbow catch."
        what_it_means = "A bent elbow lets you 'grip' more water and pull more effectively."
        how_to_improve = None
    elif avg_angle >= 70 and avg_angle < 90:
        rating = "good"
        explanation = f"Your {side} elbow averages {avg_angle:.0f}° - good bend, could be slightly higher."
        what_it_means = "You're catching water well. A bit more bend would increase your 'paddle' size."
        how_to_improve = "Try fingertip drag drill, focusing on keeping elbow high during recovery and entry."
    elif avg_angle < 70:
        rating = "needs_work"
        explanation = f"Your {side} elbow is quite bent at {avg_angle:.0f}° - almost too much."
        what_it_means = "Very bent elbows can mean you're 'slipping' water instead of pushing it back."
        how_to_improve = "Focus on 'pressing' back, not down. Imagine pulling yourself over a barrel."
    else:
        rating = "needs_work"
        explanation = f"Your {side} elbow is quite straight at {avg_angle:.0f}° - classic 'dropped elbow'."
        what_it_means = "A straight arm pushes water down, not back. You're working hard but not going forward."
        how_to_improve = "Scull drills and catch-up with pause will help develop the 'high elbow' feel."
    
    return PlainLanguageMetric(
        name=f"{side.title()} Elbow Position",
        technical_name=f"Elbow Angle ({side})",
        value=avg_angle,
        rating=rating,
        explanation=explanation,
        what_it_means=what_it_means,
        how_to_improve=how_to_improve,
    )


def generate_timeline_feedback(
    metrics: dict[str, Any],
    fps: float = 30.0,
    segment_duration: float = 10.0,
) -> list[TimelineSegment]:
    """
    Break video into segments and provide per-segment feedback.
    """
    frame_indices = metrics.get("frame_indices", [])
    if not frame_indices:
        return []
    
    segments = []
    total_frames = len(frame_indices)
    frames_per_segment = int(fps * segment_duration)
    
    # Get per-frame data
    body_roll = metrics.get("body_roll", [])
    elbow_left = metrics.get("joint_angles", {}).get("elbow_left", [])
    elbow_right = metrics.get("joint_angles", {}).get("elbow_right", [])
    hand_left_vel = metrics.get("velocities", {}).get("hand_left", [])
    hand_right_vel = metrics.get("velocities", {}).get("hand_right", [])
    
    segment_idx = 0
    for start_idx in range(0, total_frames, frames_per_segment):
        end_idx = min(start_idx + frames_per_segment, total_frames)
        
        start_time = start_idx / fps
        end_time = end_idx / fps
        start_frame = frame_indices[start_idx] if start_idx < len(frame_indices) else 0
        end_frame = frame_indices[end_idx - 1] if end_idx <= len(frame_indices) else frame_indices[-1]
        
        # Analyze this segment
        issues = []
        positives = []
        
        # Check body roll in segment
        if body_roll:
            segment_roll = body_roll[start_idx:end_idx]
            if segment_roll:
                avg_roll = np.mean([abs(r) for r in segment_roll])
                if avg_roll < 15:
                    issues.append("body swimming flat")
                elif avg_roll > 50:
                    issues.append("over-rotating")
                else:
                    positives.append("good rotation")
        
        # Check elbow angles
        if elbow_left and elbow_right:
            seg_elbow_l = [a for a in elbow_left[start_idx:end_idx] if a > 0]
            seg_elbow_r = [a for a in elbow_right[start_idx:end_idx] if a > 0]
            
            if seg_elbow_l:
                avg_l = np.mean(seg_elbow_l)
                if avg_l > 150:
                    issues.append("left elbow dropping")
                elif avg_l < 60:
                    issues.append("left arm too bent")
            
            if seg_elbow_r:
                avg_r = np.mean(seg_elbow_r)
                if avg_r > 150:
                    issues.append("right elbow dropping")
                elif avg_r < 60:
                    issues.append("right arm too bent")
        
        # Check velocity consistency
        if hand_left_vel and hand_right_vel:
            seg_vel_l = hand_left_vel[start_idx:end_idx]
            seg_vel_r = hand_right_vel[start_idx:end_idx]
            
            if seg_vel_l and seg_vel_r:
                avg_vel = np.mean(seg_vel_l + seg_vel_r)
                max_vel = max(max(seg_vel_l), max(seg_vel_r))
                
                if max_vel > 0 and avg_vel > 0:
                    consistency = max_vel / avg_vel
                    if consistency > 3:
                        issues.append("inconsistent stroke power")
                    elif consistency < 1.5:
                        positives.append("consistent power")
        
        # Determine overall status
        if len(issues) == 0:
            status = "excellent" if len(positives) > 0 else "good"
            title = "Looking Good!"
            feedback = f"Strong technique in this section. {', '.join(positives).capitalize() if positives else 'Keep it up!'}"
        elif len(issues) == 1:
            status = "needs_work"
            title = "Minor Adjustment Needed"
            feedback = f"Watch for {issues[0]}. {positives[0].capitalize() if positives else 'Other aspects look fine'}."
        else:
            status = "needs_work"
            title = "Focus Area"
            feedback = f"Issues spotted: {', '.join(issues)}. Work on these in your next session."
        
        segments.append(TimelineSegment(
            start_time=round(start_time, 1),
            end_time=round(end_time, 1),
            start_frame=start_frame,
            end_frame=end_frame,
            status=status,
            title=title,
            feedback=feedback,
            metric_focus=issues[0] if issues else None,
        ))
        
        segment_idx += 1
    
    return segments


def generate_plain_language_metrics(metrics: dict[str, Any]) -> list[PlainLanguageMetric]:
    """Generate plain-language explanations for all key metrics."""
    explanations = []
    
    # Symmetry
    symmetry = metrics.get("symmetry_index", 0)
    if symmetry > 0:
        explanations.append(explain_symmetry(symmetry))
    
    # Stroke rate
    stroke_rate = metrics.get("stroke_rate", 0)
    if stroke_rate > 0:
        explanations.append(explain_stroke_rate(stroke_rate))
    
    # Body roll
    body_roll = metrics.get("body_roll", [])
    if body_roll:
        avg_roll = np.mean([abs(r) for r in body_roll if r != 0])
        if not np.isnan(avg_roll):
            explanations.append(explain_body_roll(avg_roll))
    
    # Elbow angles
    joint_angles = metrics.get("joint_angles", {})
    elbow_left = joint_angles.get("elbow_left", [])
    elbow_right = joint_angles.get("elbow_right", [])
    
    if elbow_left:
        valid_angles = [a for a in elbow_left if a > 0]
        if valid_angles:
            avg_left = np.mean(valid_angles)
            explanations.append(explain_elbow_angle(avg_left, "left"))
    
    if elbow_right:
        valid_angles = [a for a in elbow_right if a > 0]
        if valid_angles:
            avg_right = np.mean(valid_angles)
            explanations.append(explain_elbow_angle(avg_right, "right"))
    
    return explanations


def generate_coaching_summary(
    metrics: dict[str, Any],
    timeline_segments: list[TimelineSegment],
    plain_metrics: list[PlainLanguageMetric],
) -> dict[str, Any]:
    """
    Generate a complete coaching-focused feedback package.
    """
    # Count segment statuses
    excellent_segments = sum(1 for s in timeline_segments if s.status == "excellent")
    good_segments = sum(1 for s in timeline_segments if s.status == "good")
    needs_work_segments = sum(1 for s in timeline_segments if s.status == "needs_work")
    total_segments = len(timeline_segments)
    
    # Calculate overall score (0-10)
    if total_segments > 0:
        score = (excellent_segments * 10 + good_segments * 7 + needs_work_segments * 4) / total_segments
    else:
        score = 5.0
    
    # Adjust score based on metrics
    excellent_metrics = sum(1 for m in plain_metrics if m.rating == "excellent")
    good_metrics = sum(1 for m in plain_metrics if m.rating == "good")
    total_metrics = len(plain_metrics)
    
    if total_metrics > 0:
        metric_score = (excellent_metrics * 10 + good_metrics * 7) / total_metrics
        score = (score + metric_score) / 2
    
    # Determine grade
    if score >= 8.5:
        grade = "A"
        grade_text = "Excellent"
    elif score >= 7:
        grade = "B"
        grade_text = "Good"
    elif score >= 5.5:
        grade = "C"
        grade_text = "Average"
    elif score >= 4:
        grade = "D"
        grade_text = "Needs Work"
    else:
        grade = "F"
        grade_text = "Significant Improvement Needed"
    
    # Identify top strengths and weaknesses
    strengths = [m for m in plain_metrics if m.rating in ("excellent", "good")]
    weaknesses = [m for m in plain_metrics if m.rating in ("needs_work", "poor")]
    
    # Build executive summary
    if strengths and not weaknesses:
        summary = f"Great swim! Your technique is solid across the board. "
    elif weaknesses and not strengths:
        summary = f"There's room for improvement. Let's focus on the fundamentals. "
    elif strengths and weaknesses:
        summary = f"Good foundation with some areas to polish. "
    else:
        summary = "Analysis complete. "
    
    if strengths:
        summary += f"Your {strengths[0].name.lower()} is particularly strong. "
    if weaknesses:
        summary += f"Priority focus: {weaknesses[0].name.lower()}. "
    
    return {
        "score": round(score, 1),
        "grade": grade,
        "grade_text": grade_text,
        "executive_summary": summary.strip(),
        "strengths": [
            {"name": m.name, "explanation": m.explanation}
            for m in strengths[:3]
        ],
        "improvements": [
            {"name": m.name, "explanation": m.explanation, "tip": m.how_to_improve}
            for m in weaknesses[:3]
        ],
        "timeline_segments": [
            {
                "start_time": s.start_time,
                "end_time": s.end_time,
                "start_frame": s.start_frame,
                "end_frame": s.end_frame,
                "status": s.status,
                "title": s.title,
                "feedback": s.feedback,
            }
            for s in timeline_segments
        ],
        "metrics_explained": [
            {
                "name": m.name,
                "technical_name": m.technical_name,
                "value": m.value,
                "rating": m.rating,
                "explanation": m.explanation,
                "what_it_means": m.what_it_means,
                "how_to_improve": m.how_to_improve,
            }
            for m in plain_metrics
        ],
    }

