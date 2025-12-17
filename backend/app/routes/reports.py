"""
Blueprint for report retrieval endpoints.
"""

from __future__ import annotations

import csv
import io
from flask import Blueprint, Response, jsonify, request, send_file

from ..services.report_repository import fetch_report_paths
from ..services.metrics_repository import get_metrics_for_video as fetch_metrics

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/reports/<string:video_id>")
def download_report(video_id: str):
    """
    Return the requested report artifact (HTML, PDF, or CSV) for the given video.
    """
    report_format = request.args.get("format", "html").lower()
    
    # Handle CSV export separately (generated on-the-fly)
    if report_format == "csv":
        return export_csv(video_id)
    
    report_paths = fetch_report_paths(video_id)

    if not report_paths:
        return jsonify({"error": "Report not available"}), 404

    if report_format not in report_paths:
        return jsonify({"error": f"Report format '{report_format}' unavailable"}), 400

    return send_file(report_paths[report_format], as_attachment=True)


def export_csv(video_id: str) -> Response:
    """Generate CSV export of metrics data."""
    metrics = fetch_metrics(video_id)
    
    if not metrics:
        return jsonify({"error": "Metrics not available"}), 404
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Summary metrics
    writer.writerow(["=== SUMMARY METRICS ==="])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Stroke Rate (SPM)", metrics.get("stroke_rate", "")])
    writer.writerow(["Stroke Length (m)", metrics.get("stroke_length", "")])
    writer.writerow(["Symmetry Index", metrics.get("symmetry_index", "")])
    writer.writerow(["Average Velocity", metrics.get("avg_velocity", "")])
    writer.writerow(["Max Velocity", metrics.get("max_velocity", "")])
    writer.writerow([])
    
    # Frame-by-frame data
    frame_indices = metrics.get("frame_indices", [])
    if frame_indices:
        writer.writerow(["=== FRAME-BY-FRAME DATA ==="])
        
        # Build header
        headers = ["Frame"]
        joint_angles = metrics.get("joint_angles", {})
        velocities = metrics.get("velocities", {})
        
        if joint_angles.get("elbow_left"):
            headers.extend(["Elbow Left (°)", "Elbow Right (°)"])
        if joint_angles.get("shoulder_left"):
            headers.extend(["Shoulder Left (°)", "Shoulder Right (°)"])
        if joint_angles.get("knee_left"):
            headers.extend(["Knee Left (°)", "Knee Right (°)"])
        if metrics.get("body_roll"):
            headers.append("Body Roll (°)")
        if velocities.get("hand_left"):
            headers.extend(["Hand Left Vel", "Hand Right Vel"])
        if metrics.get("kick_timing"):
            headers.append("Kick Timing")
        if metrics.get("body_alignment"):
            headers.append("Body Alignment (°)")
        
        writer.writerow(headers)
        
        # Write data rows
        for i, frame in enumerate(frame_indices):
            row = [frame]
            
            if joint_angles.get("elbow_left"):
                row.append(joint_angles["elbow_left"][i] if i < len(joint_angles["elbow_left"]) else "")
                row.append(joint_angles.get("elbow_right", [])[i] if i < len(joint_angles.get("elbow_right", [])) else "")
            if joint_angles.get("shoulder_left"):
                row.append(joint_angles["shoulder_left"][i] if i < len(joint_angles["shoulder_left"]) else "")
                row.append(joint_angles.get("shoulder_right", [])[i] if i < len(joint_angles.get("shoulder_right", [])) else "")
            if joint_angles.get("knee_left"):
                row.append(joint_angles["knee_left"][i] if i < len(joint_angles["knee_left"]) else "")
                row.append(joint_angles.get("knee_right", [])[i] if i < len(joint_angles.get("knee_right", [])) else "")
            if metrics.get("body_roll"):
                row.append(metrics["body_roll"][i] if i < len(metrics["body_roll"]) else "")
            if velocities.get("hand_left"):
                row.append(velocities["hand_left"][i] if i < len(velocities["hand_left"]) else "")
                row.append(velocities.get("hand_right", [])[i] if i < len(velocities.get("hand_right", [])) else "")
            if metrics.get("kick_timing"):
                row.append(metrics["kick_timing"][i] if i < len(metrics["kick_timing"]) else "")
            if metrics.get("body_alignment"):
                row.append(metrics["body_alignment"][i] if i < len(metrics["body_alignment"]) else "")
            
            writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=swim-metrics-{video_id}.csv"}
    )

