import PropTypes from "prop-types";
import Plot from "react-plotly.js";

/**
 * Generic chart component that renders line charts for biomechanical metrics.
 */
function MetricsChart({ title, series, xAxis, yAxisLabel = "Value" }) {
  if (!xAxis || xAxis.length === 0 || !series || series.length === 0) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#999" }}>
        No data available for {title}
      </div>
    );
  }

  const data = series.map((item) => ({
    x: xAxis.slice(0, item.values.length),
    y: item.values,
    type: "scatter",
    mode: "lines",
    name: item.label,
    line: { width: 2 },
    hovertemplate: `<b>${item.label}</b><br>Frame: %{x}<br>Value: %{y:.2f}<extra></extra>`
  }));

  return (
    <div style={{ marginBottom: "20px", backgroundColor: "#1e293b", borderRadius: "8px", padding: "10px" }}>
      <Plot
        data={data}
        layout={{
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
        }}
        useResizeHandler
        style={{ width: "100%", height: "300px" }}
        config={{ 
          displaylogo: false, 
          responsive: true,
          modeBarButtonsToRemove: ["pan2d", "lasso2d", "select2d"],
          displayModeBar: true
        }}
      />
    </div>
  );
}

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

