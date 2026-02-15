import { memo, useMemo } from "react";
import PropTypes from "prop-types";
import "./MetricsSummary.css";

/**
 * Highlights headline metrics such as stroke rate, symmetry, and body roll.
 * Memoized to prevent unnecessary re-renders.
 */
const MetricsSummary = memo(function MetricsSummary({ metrics = {} }) {
  // Memoize summary items to prevent recalculation
  const summaryItems = useMemo(() => [
    { label: "Stroke Rate", value: metrics.stroke_rate?.toFixed(1), unit: "spm" },
    { label: "Stroke Length", value: metrics.stroke_length?.toFixed(2), unit: "m" },
    { label: "Symmetry Index", value: metrics.symmetry_index?.toFixed(2), unit: "" },
    { label: "Streamline Score", value: metrics.avg_streamline?.toFixed(1), unit: "/100" },
    { label: "Propulsion Efficiency", value: metrics.propulsion_efficiency?.toFixed(1), unit: "%" },
    { label: "Hand Slipping", value: metrics.slipping_percentage?.toFixed(1), unit: "%" },
    { label: "Avg Velocity", value: metrics.avg_velocity?.toFixed(2), unit: "" },
    { label: "Max Velocity", value: metrics.max_velocity?.toFixed(2), unit: "" }
  ], [metrics]);

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
});

MetricsSummary.propTypes = {
  metrics: PropTypes.shape({
    stroke_rate: PropTypes.number,
    stroke_length: PropTypes.number,
    symmetry_index: PropTypes.number
  })
};

export default MetricsSummary;

