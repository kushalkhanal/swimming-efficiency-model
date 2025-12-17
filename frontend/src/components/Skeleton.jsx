import "./Skeleton.css";

/**
 * Skeleton loading placeholder components
 */

export function Skeleton({ width, height, variant = "rectangular", className = "" }) {
  return (
    <div
      className={`skeleton skeleton--${variant} ${className}`}
      style={{ width, height }}
    />
  );
}

export function VideoSkeleton() {
  return (
    <div className="skeleton-video">
      <Skeleton variant="rectangular" width="100%" height="400px" />
      <div className="skeleton-video__controls">
        <Skeleton variant="circular" width="48px" height="48px" />
        <Skeleton variant="rectangular" width="100%" height="8px" />
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="skeleton-chart">
      <Skeleton variant="text" width="40%" height="24px" />
      <div className="skeleton-chart__bars">
        {[...Array(8)].map((_, i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            width="10%"
            height={`${30 + Math.random() * 70}%`}
          />
        ))}
      </div>
      <Skeleton variant="rectangular" width="100%" height="2px" />
    </div>
  );
}

export function MetricsSummarySkeleton() {
  return (
    <div className="skeleton-metrics-summary">
      <Skeleton variant="text" width="60%" height="28px" />
      <div className="skeleton-metrics-summary__grid">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="skeleton-metrics-summary__item">
            <Skeleton variant="text" width="80%" height="16px" />
            <Skeleton variant="text" width="50%" height="32px" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function FeedbackSkeleton() {
  return (
    <div className="skeleton-feedback">
      <Skeleton variant="text" width="50%" height="24px" />
      <div className="skeleton-feedback__lines">
        {[...Array(5)].map((_, i) => (
          <Skeleton
            key={i}
            variant="text"
            width={`${60 + Math.random() * 40}%`}
            height="16px"
          />
        ))}
      </div>
      <Skeleton variant="rectangular" width="100%" height="80px" className="skeleton-feedback__box" />
    </div>
  );
}

export function ProcessingProgress({ stage, progress, message }) {
  const stages = [
    { id: "upload", label: "Uploading" },
    { id: "detection", label: "Detecting Swimmers" },
    { id: "pose", label: "Pose Estimation" },
    { id: "metrics", label: "Computing Metrics" },
    { id: "report", label: "Generating Report" },
  ];

  const currentIndex = stages.findIndex((s) => s.id === stage);

  return (
    <div className="processing-progress">
      <div className="processing-progress__header">
        <span className="processing-progress__title">Processing Video</span>
        <span className="processing-progress__percent">{Math.round(progress)}%</span>
      </div>
      
      <div className="processing-progress__bar">
        <div
          className="processing-progress__fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="processing-progress__stages">
        {stages.map((s, i) => (
          <div
            key={s.id}
            className={`processing-progress__stage ${
              i < currentIndex ? "completed" : i === currentIndex ? "active" : ""
            }`}
          >
            <div className="processing-progress__dot">
              {i < currentIndex ? "✓" : i + 1}
            </div>
            <span className="processing-progress__label">{s.label}</span>
          </div>
        ))}
      </div>

      {message && (
        <div className="processing-progress__message">{message}</div>
      )}
    </div>
  );
}

