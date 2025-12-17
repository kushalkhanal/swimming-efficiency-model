import PropTypes from "prop-types";
import "./MetricsSummary.css";

/**
 * Highlights headline metrics such as stroke rate, symmetry, and body roll.
 */
function MetricsSummary({ metrics = {} }) {
  const summaryItems = [
    { label: "Stroke Rate", value: metrics.stroke_rate?.toFixed(1), unit: "spm" },
    { label: "Stroke Length", value: metrics.stroke_length?.toFixed(2), unit: "m" },
    { label: "Symmetry Index", value: metrics.symmetry_index?.toFixed(2), unit: "" },
    { label: "Avg Velocity", value: metrics.avg_velocity?.toFixed(2), unit: "" },
    { label: "Max Velocity", value: metrics.max_velocity?.toFixed(2), unit: "" }
  ];

  return (
    <div className="metrics-summary">
      {summaryItems.map((item) => (
        <div key={item.label} className="metrics-summary-card">
          <span>{item.label}</span>
          <strong>
            {item.value ?? "--"} {item.unit}
          </strong>
        </div>
      ))}
    </div>
  );
}

MetricsSummary.propTypes = {
  metrics: PropTypes.shape({
    stroke_rate: PropTypes.number,
    stroke_length: PropTypes.number,
    symmetry_index: PropTypes.number
  })
};

export default MetricsSummary;

