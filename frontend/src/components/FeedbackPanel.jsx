import PropTypes from "prop-types";
import "./FeedbackPanel.css";

/**
 * Displays coaching-focused feedback with plain-language explanations
 * and timeline-based analysis.
 */
function FeedbackPanel({ summary = "", phaseBreakdown = null, keyMetrics = null, coaching = null }) {
  const formatPhaseBreakdown = (breakdown) => {
    if (!breakdown || typeof breakdown === "string") return breakdown;
    return Object.entries(breakdown)
      .map(([phase, data]) => {
        if (typeof data === "object" && data.frames !== undefined) {
          return `${phase}: ${data.frames} frames (${data.percentage})`;
        }
        return `${phase}: ${data}`;
      })
      .join("\n");
  };

  const getRatingColor = (rating) => {
    switch (rating) {
      case "excellent": return "#10b981";
      case "good": return "#3b82f6";
      case "needs_work": return "#f59e0b";
      case "poor": return "#ef4444";
      default: return "#94a3b8";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "excellent": return "#10b981";
      case "good": return "#3b82f6";
      case "needs_work": return "#f59e0b";
      default: return "#94a3b8";
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // If we have coaching data, show the new coaching-focused UI
  if (coaching) {
    return (
      <section className="feedback-panel coaching-panel">
        {/* Executive Summary */}
        <div className="coaching-header">
          <div className="coaching-score">
            <span className="score-value">{coaching.score}</span>
            <span className="score-label">/ 10</span>
          </div>
          <div className="coaching-grade">
            <span className="grade-letter">{coaching.grade}</span>
            <span className="grade-text">{coaching.grade_text}</span>
          </div>
        </div>
        
        <p className="executive-summary">{coaching.executive_summary}</p>

        {/* Strengths */}
        {coaching.strengths?.length > 0 && (
          <div className="coaching-section">
            <h3>💪 Your Strengths</h3>
            <div className="coaching-list">
              {coaching.strengths.map((s, i) => (
                <div key={i} className="coaching-item strength">
                  <span className="item-name">{s.name}</span>
                  <p className="item-explanation">{s.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Areas to Improve */}
        {coaching.improvements?.length > 0 && (
          <div className="coaching-section">
            <h3>🎯 Focus Areas</h3>
            <div className="coaching-list">
              {coaching.improvements.map((imp, i) => (
                <div key={i} className="coaching-item improvement">
                  <span className="item-name">{imp.name}</span>
                  <p className="item-explanation">{imp.explanation}</p>
                  {imp.tip && (
                    <p className="item-tip">
                      <strong>Drill:</strong> {imp.tip}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Feedback */}
        {coaching.timeline_segments?.length > 0 && (
          <div className="coaching-section">
            <h3>📍 Timeline Breakdown</h3>
            <div className="timeline-container">
              {coaching.timeline_segments.map((seg, i) => (
                <div 
                  key={i} 
                  className={`timeline-segment ${seg.status}`}
                  style={{ borderLeftColor: getStatusColor(seg.status) }}
                >
                  <div className="segment-time">
                    {formatTime(seg.start_time)} - {formatTime(seg.end_time)}
                  </div>
                  <div className="segment-title">{seg.title}</div>
                  <div className="segment-feedback">{seg.feedback}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Plain Language Metrics */}
        {coaching.metrics_explained?.length > 0 && (
          <div className="coaching-section">
            <h3>📊 Metrics Explained</h3>
            <div className="metrics-explained">
              {coaching.metrics_explained.map((m, i) => (
                <div key={i} className="metric-card-explained">
                  <div className="metric-header">
                    <span className="metric-name">{m.name}</span>
                    <span 
                      className="metric-rating"
                      style={{ backgroundColor: getRatingColor(m.rating) }}
                    >
                      {m.rating.replace("_", " ")}
                    </span>
                  </div>
                  <p className="metric-explanation">{m.explanation}</p>
                  <p className="metric-meaning">{m.what_it_means}</p>
                  {m.how_to_improve && (
                    <p className="metric-improve">
                      <strong>How to improve:</strong> {m.how_to_improve}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    );
  }

  // Fallback to original UI if no coaching data
  return (
    <section className="feedback-panel">
      <h2>Automated Feedback</h2>
      <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.6" }}>
        {summary || "Insights will appear after video processing completes."}
      </div>
      {keyMetrics && (
        <div style={{ marginTop: "15px", padding: "10px", backgroundColor: "#1e293b", borderRadius: "5px" }}>
          <h3 style={{ fontSize: "14px", marginBottom: "8px", color: "#94a3b8" }}>Key Metrics:</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "5px" }}>
            {Object.entries(keyMetrics).map(([key, value]) => (
              <div key={key} style={{ fontSize: "13px" }}>
                <strong>{key.replace(/_/g, " ")}:</strong> {value}
              </div>
            ))}
          </div>
        </div>
      )}
      {phaseBreakdown && (
        <div style={{ marginTop: "15px" }}>
          <h3 style={{ fontSize: "14px", marginBottom: "8px", color: "#94a3b8" }}>Stroke Phase Breakdown:</h3>
          <pre aria-label="Stroke phase breakdown" style={{ 
            backgroundColor: "#1e293b", 
            padding: "10px", 
            borderRadius: "5px",
            fontSize: "13px",
            overflowX: "auto"
          }}>
            {formatPhaseBreakdown(phaseBreakdown)}
          </pre>
        </div>
      )}
    </section>
  );
}

FeedbackPanel.propTypes = {
  summary: PropTypes.string,
  phaseBreakdown: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  keyMetrics: PropTypes.object,
  coaching: PropTypes.object,
};

export default FeedbackPanel;

