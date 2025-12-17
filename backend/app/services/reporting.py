"""
Report generation utilities for PDF and HTML exports.

Generates comprehensive biomechanical analysis reports with charts, metrics,
and narrative feedback.
"""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Template
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..db.repositories import ReportRepository

report_repo = ReportRepository()


def create_chart_image(metrics: dict[str, Any], chart_type: str, output_path: Path) -> str:
    """Create a matplotlib chart and save as image, return base64 string."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#1e293b")
    ax.set_facecolor("#0f172a")
    
    frame_indices = metrics.get("frame_indices", [])
    
    if chart_type == "joint_angles_elbow":
        left = metrics.get("joint_angles", {}).get("elbow_left", [])
        right = metrics.get("joint_angles", {}).get("elbow_right", [])
        if left and right:
            ax.plot(frame_indices[:len(left)], left, label="Left Elbow", linewidth=2, color="#3b82f6")
            ax.plot(frame_indices[:len(right)], right, label="Right Elbow", linewidth=2, color="#ef4444")
            ax.set_title("Elbow Joint Angles", color="white", fontsize=14, fontweight="bold")
            ax.set_xlabel("Frame Number", color="white")
            ax.set_ylabel("Angle (degrees)", color="white")
            ax.legend()
            ax.grid(True, alpha=0.3, color="white")
            ax.tick_params(colors="white")
    
    elif chart_type == "body_roll":
        roll = metrics.get("body_roll", [])
        if roll:
            ax.plot(frame_indices[:len(roll)], roll, linewidth=2, color="#10b981")
            ax.set_title("Body Roll", color="white", fontsize=14, fontweight="bold")
            ax.set_xlabel("Frame Number", color="white")
            ax.set_ylabel("Roll (degrees)", color="white")
            ax.grid(True, alpha=0.3, color="white")
            ax.tick_params(colors="white")
    
    elif chart_type == "hand_velocities":
        left = metrics.get("velocities", {}).get("hand_left", [])
        right = metrics.get("velocities", {}).get("hand_right", [])
        if left and right:
            ax.plot(frame_indices[:len(left)], left, label="Left Hand", linewidth=2, color="#3b82f6")
            ax.plot(frame_indices[:len(right)], right, label="Right Hand", linewidth=2, color="#ef4444")
            ax.set_title("Hand Velocities", color="white", fontsize=14, fontweight="bold")
            ax.set_xlabel("Frame Number", color="white")
            ax.set_ylabel("Velocity", color="white")
            ax.legend()
            ax.grid(True, alpha=0.3, color="white")
            ax.tick_params(colors="white")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#1e293b")
    plt.close()
    
    # Return base64 for HTML embedding
    with open(output_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def generate_html_report(
    video_id: str,
    metrics: dict[str, Any],
    narrative: dict[str, Any],
    report_dir: Path,
) -> Path:
    """Generate comprehensive HTML report."""
    html_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swimming Biomechanics Analysis Report - {{ video_id }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: #1e293b;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #3b82f6;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #94a3b8;
            margin-bottom: 40px;
        }
        .section {
            margin-bottom: 40px;
            background: #0f172a;
            padding: 30px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        h2 {
            color: #60a5fa;
            font-size: 1.8em;
            margin-bottom: 20px;
        }
        h3 {
            color: #94a3b8;
            font-size: 1.3em;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #1e293b;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #334155;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #3b82f6;
            margin: 10px 0;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .feedback {
            background: #1e293b;
            padding: 20px;
            border-radius: 8px;
            white-space: pre-wrap;
            line-height: 1.8;
        }
        .chart {
            margin: 30px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .phase-breakdown {
            background: #1e293b;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background: #0f172a;
            color: #60a5fa;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏊 Swimming Biomechanics Analysis</h1>
        <p class="subtitle">Report generated on {{ report_date }}</p>
        
        <div class="section">
            <h2>Key Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Stroke Rate</div>
                    <div class="metric-value">{{ metrics.stroke_rate | round(1) }} SPM</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Symmetry Index</div>
                    <div class="metric-value">{{ metrics.symmetry_index | round(2) }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Stroke Length</div>
                    <div class="metric-value">{{ metrics.stroke_length | round(2) }} m</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Velocity</div>
                    <div class="metric-value">{{ metrics.avg_velocity | round(2) }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Max Velocity</div>
                    <div class="metric-value">{{ metrics.max_velocity | round(2) }}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Automated Feedback</h2>
            <div class="feedback">{{ narrative.summary }}</div>
        </div>
        
        {% if narrative.phase_breakdown %}
        <div class="section">
            <h2>Stroke Phase Breakdown</h2>
            <div class="phase-breakdown">
                {% for phase, data in narrative.phase_breakdown.items() %}
                <div><strong>{{ phase }}:</strong> {{ data.frames }} frames ({{ data.percentage }})</div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>Visualizations</h2>
            {% if chart_elbow %}
            <div class="chart">
                <h3>Elbow Joint Angles</h3>
                <img src="data:image/png;base64,{{ chart_elbow }}" alt="Elbow Joint Angles">
            </div>
            {% endif %}
            
            {% if chart_roll %}
            <div class="chart">
                <h3>Body Roll</h3>
                <img src="data:image/png;base64,{{ chart_roll }}" alt="Body Roll">
            </div>
            {% endif %}
            
            {% if chart_velocity %}
            <div class="chart">
                <h3>Hand Velocities</h3>
                <img src="data:image/png;base64,{{ chart_velocity }}" alt="Hand Velocities">
            </div>
            {% endif %}
        </div>
        
        <div class="section">
            <h2>Joint Angles Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Joint</th>
                        <th>Left Avg</th>
                        <th>Right Avg</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
                    {% for joint in ['elbow', 'shoulder', 'knee'] %}
                    <tr>
                        <td>{{ joint | capitalize }}</td>
                        <td>{{ joint_angles_left[joint] | round(1) }}°</td>
                        <td>{{ joint_angles_right[joint] | round(1) }}°</td>
                        <td>{{ (joint_angles_left[joint] - joint_angles_right[joint]) | abs | round(1) }}°</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Video ID: {{ video_id }}</p>
            <p>Generated by Swimming Biomechanics Analysis Platform</p>
        </div>
    </div>
</body>
</html>
    """)
    
    # Create chart images
    chart_dir = report_dir / "charts"
    chart_dir.mkdir(exist_ok=True)
    
    chart_elbow = None
    chart_roll = None
    chart_velocity = None
    
    try:
        chart_elbow = create_chart_image(metrics, "joint_angles_elbow", chart_dir / "elbow.png")
    except Exception:
        pass
    
    try:
        chart_roll = create_chart_image(metrics, "body_roll", chart_dir / "roll.png")
    except Exception:
        pass
    
    try:
        chart_velocity = create_chart_image(metrics, "hand_velocities", chart_dir / "velocity.png")
    except Exception:
        pass
    
    # Calculate joint angle averages
    joint_angles = metrics.get("joint_angles", {})
    joint_angles_left = {
        "elbow": np.mean([a for a in joint_angles.get("elbow_left", []) if a > 0]) if joint_angles.get("elbow_left") else 0.0,
        "shoulder": np.mean([a for a in joint_angles.get("shoulder_left", []) if a > 0]) if joint_angles.get("shoulder_left") else 0.0,
        "knee": np.mean([a for a in joint_angles.get("knee_left", []) if a > 0]) if joint_angles.get("knee_left") else 0.0,
    }
    joint_angles_right = {
        "elbow": np.mean([a for a in joint_angles.get("elbow_right", []) if a > 0]) if joint_angles.get("elbow_right") else 0.0,
        "shoulder": np.mean([a for a in joint_angles.get("shoulder_right", []) if a > 0]) if joint_angles.get("shoulder_right") else 0.0,
        "knee": np.mean([a for a in joint_angles.get("knee_right", []) if a > 0]) if joint_angles.get("knee_right") else 0.0,
    }
    
    # Render HTML
    html_content = html_template.render(
        video_id=video_id,
        report_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        metrics=metrics,
        narrative=narrative,
        chart_elbow=chart_elbow,
        chart_roll=chart_roll,
        chart_velocity=chart_velocity,
        joint_angles_left=joint_angles_left,
        joint_angles_right=joint_angles_right,
    )
    
    html_path = report_dir / "report.html"
    html_path.write_text(html_content, encoding="utf-8")
    
    return html_path


def generate_pdf_report(
    video_id: str,
    metrics: dict[str, Any],
    narrative: dict[str, Any],
    report_dir: Path,
) -> Path:
    """Generate comprehensive PDF report."""
    pdf_path = report_dir / "report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#3b82f6"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#60a5fa"),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("Swimming Biomechanics Analysis", title_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    
    # Key Metrics
    story.append(Paragraph("Key Metrics", heading_style))
    metrics_data = [
        ["Metric", "Value"],
        ["Stroke Rate", f"{metrics.get('stroke_rate', 0):.1f} SPM"],
        ["Symmetry Index", f"{metrics.get('symmetry_index', 0):.2f}"],
        ["Stroke Length", f"{metrics.get('stroke_length', 0):.2f} m"],
        ["Average Velocity", f"{metrics.get('avg_velocity', 0):.2f}"],
        ["Max Velocity", f"{metrics.get('max_velocity', 0):.2f}"],
    ]
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#60a5fa")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Feedback
    story.append(Paragraph("Automated Feedback", heading_style))
    feedback_text = narrative.get("summary", "No feedback available.")
    story.append(Paragraph(feedback_text.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 20))
    
    # Phase Breakdown
    phase_breakdown = narrative.get("phase_breakdown", {})
    if phase_breakdown:
        story.append(Paragraph("Stroke Phase Breakdown", heading_style))
        phase_data = [["Phase", "Frames", "Percentage"]]
        for phase, data in phase_breakdown.items():
            if isinstance(data, dict):
                phase_data.append([
                    phase.capitalize(),
                    str(data.get("frames", 0)),
                    data.get("percentage", "0%"),
                ])
        
        if len(phase_data) > 1:
            phase_table = Table(phase_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            phase_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#60a5fa")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#1e293b")),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
            ]))
            story.append(phase_table)
            story.append(Spacer(1, 20))
    
    # Add chart images if available
    chart_dir = report_dir / "charts"
    chart_dir.mkdir(exist_ok=True)
    
    try:
        chart_path = chart_dir / "elbow.png"
        create_chart_image(metrics, "joint_angles_elbow", chart_path)
        if chart_path.exists():
            story.append(Paragraph("Elbow Joint Angles", heading_style))
            img = Image(str(chart_path), width=6*inch, height=3.6*inch)
            story.append(img)
            story.append(Spacer(1, 20))
    except Exception:
        pass
    
    try:
        chart_path = chart_dir / "roll.png"
        create_chart_image(metrics, "body_roll", chart_path)
        if chart_path.exists():
            story.append(Paragraph("Body Roll", heading_style))
            img = Image(str(chart_path), width=6*inch, height=3.6*inch)
            story.append(img)
            story.append(Spacer(1, 20))
    except Exception:
        pass
    
    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Video ID: {video_id}", styles["Normal"]))
    story.append(Paragraph("Generated by Swimming Biomechanics Analysis Platform", styles["Normal"]))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path


def generate_report_artifacts(
    *,
    video_id: str,
    video_path: Path,
    metrics: dict,
    narrative: dict,
) -> None:
    """
    Generate comprehensive PDF and HTML reports with charts and metrics.
    """
    report_dir = Path("data/artifacts") / "reports" / video_id
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML report
    try:
        html_path = generate_html_report(video_id, metrics, narrative, report_dir)
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        html_path = None
    
    # Generate PDF report
    try:
        pdf_path = generate_pdf_report(video_id, metrics, narrative, report_dir)
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        pdf_path = None
    
    # Store report paths in database
    report_repo.upsert_report(
        video_id,
        {
            "html": str(html_path.resolve()) if html_path and html_path.exists() else None,
            "pdf": str(pdf_path.resolve()) if pdf_path and pdf_path.exists() else None,
        },
    )
