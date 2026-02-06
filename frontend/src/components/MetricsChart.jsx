import { memo, useMemo } from "react";
import PropTypes from "prop-types";
import Plot from "react-plotly.js";

/**
 * Generic chart component that renders line charts for biomechanical metrics.
 * Memoized to prevent unnecessary re-renders when props haven't changed.
 */
const MetricsChart = memo(function MetricsChart({ title, series, xAxis, yAxisLabel = "Value" }) {
  if (!xAxis || xAxis.length === 0 || !series || series.length === 0) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#999" }}>
        No data available for {title}
      </div>
    );
  }

  // Memoize chart data to prevent recalculation on every render
  const data = useMemo(() => {
    return series.map((item) => ({
      x: xAxis.slice(0, item.values.length),
      y: item.values,
      type: "scatter",
      mode: "lines",
      name: item.label,
      line: { width: 2 },
      hovertemplate: `<b>${item.label}</b><br>Frame: %{x}<br>Value: %{y:.2f}<extra></extra>`
    }));
  }, [series, xAxis]);
  
  // Memoize layout to prevent recreation
  const layout = useMemo(() => ({
    title: {
      text: title,
      font: { color: "#e2e8f0", size: 16 }
    },
    xaxis: {
      title: "Frame Number",
      titlefont: { color: "#94a3b8" },
      tickfont: { color: "#94a3b8" },
      gridcolor: "#334155"
    },
    yaxis: {
      title: yAxisLabel,
      titlefont: { color: "#94a3b8" },
      tickfont: { color: "#94a3b8" },
      gridcolor: "#334155"
    },
    paper_bgcolor: "rgba(30,41,59,1)",
    plot_bgcolor: "rgba(15,23,42,1)",
    font: { color: "#e2e8f0" },
    margin: { t: 50, l: 60, r: 20, b: 50 },
    hovermode: "x unified",
    showlegend: series.length > 1
  }), [title, yAxisLabel, series.length]);

  const plotConfig = useMemo(() => ({
    displaylogo: false,
    responsive: true,
    modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
    displayModeBar: true
  }), []);

  return (
    <div style={{ marginBottom: "20px", backgroundColor: "#1e293b", borderRadius: "8px", padding: "10px" }}>
      <Plot
        data={data}
        layout={layout}
        useResizeHandler
        style={{ width: "100%", height: "300px" }}
        config={plotConfig}
      />
    </div>
  );
});

MetricsChart.propTypes = {
  title: PropTypes.string.isRequired,
  series: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      values: PropTypes.arrayOf(PropTypes.number).isRequired
    })
  ).isRequired,
  xAxis: PropTypes.arrayOf(PropTypes.number).isRequired,
  yAxisLabel: PropTypes.string
};

export default MetricsChart;

