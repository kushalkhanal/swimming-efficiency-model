import { useState, useEffect, useRef, lazy, Suspense, useMemo, useCallback } from "react";
import ErrorBoundary from "../components/ErrorBoundary";
import SwimAnalysis from "../components/SwimAnalysis";
import TestLayout from "../components/TestLayout";
import MetricsSummary from "../components/MetricsSummary";
import MetricsChart from "../components/MetricsChart";
import FeedbackPanel from "../components/FeedbackPanel";
import ReportExport from "../components/ReportExport";

// Lazy load heavy components
const VideoTrimmer = lazy(() => import("../components/VideoTrimmer"));
import {
  VideoSkeleton,
  ChartSkeleton,
  MetricsSummarySkeleton,
  FeedbackSkeleton,
  ProcessingProgress,
} from "../components/Skeleton";
import { useFrameData } from "../hooks/useFrameData";
import { useProcessingProgress } from "../hooks/useProcessingProgress";
import { useFormattedKeypoints } from "../hooks/useFormattedKeypoints";
import { useVideoMetrics } from "../hooks/useVideoMetrics";
import { useNavigate } from "react-router-dom";

import "./DashboardPage.css";

function DashboardPage() {
  const navigate = useNavigate();
  const [currentVideoId, setCurrentVideoId] = useState("");
  const [currentFrame, setCurrentFrame] = useState(0);
  const [showTrimmer, setShowTrimmer] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const [trimSettings, setTrimSettings] = useState({ startTime: 0, endTime: null });
  const [showTestLayout, setShowTestLayout] = useState(false); // Toggle for test layout

  const { frameOverlay, uploadVideo, uploadError, isUploading, clearError } = useFrameData(
    currentVideoId
  );

  const useAdvancedView = !showTestLayout && frameOverlay?.videoSrc; // Always use advanced view when video is loaded (unless test layout is shown)
  const {
    stage,
    progress,
    message,
    isProcessing,
    startProcessing,
    setUploadProgress,
    resetProgress
  } = useProcessingProgress();
  const { keypointsData: formattedKeypoints, isLoading: keypointsLoading, refetch: refetchKeypoints } = useFormattedKeypoints(currentVideoId);
  const { metrics, narrative, isLoading: metricsLoading, refetch: refetchMetrics } = useVideoMetrics(currentVideoId);


  // Memoize callbacks to prevent unnecessary re-renders
  const handleFileChange = useCallback((event) => {
    const file = event.target.files?.[0];
    if (file) {
      clearError();
      setPendingFile(file);
      setShowTrimmer(true);
    }
    // Reset input to allow uploading same file again
    event.target.value = "";
  }, [clearError]);

  const handleTrimConfirm = useCallback((settings) => {
    setShowTrimmer(false);
    if (pendingFile) {
      // Store trim settings for video player
      setTrimSettings({
        startTime: settings.startTime,
        endTime: settings.endTime,
      });
      startProcessing(null);
      uploadVideo(pendingFile, (videoId) => {
        setCurrentVideoId(videoId);

        // Store video in localStorage for comparison feature
        const storedVideos = JSON.parse(localStorage.getItem('uploadedVideos') || '[]');
        const newVideo = {
          id: videoId,
          name: pendingFile.name,
          // Use API endpoint instead of blob URL for persistence
          src: `http://localhost:8000/api/v1/videos/${videoId}`,
          uploadedAt: new Date().toISOString(),
        };
        storedVideos.push(newVideo);
        localStorage.setItem('uploadedVideos', JSON.stringify(storedVideos));
      }, setUploadProgress, settings);
      setPendingFile(null);
    }
  }, [pendingFile, startProcessing, uploadVideo, setUploadProgress]);

  const handleTrimCancel = useCallback(() => {
    setShowTrimmer(false);
    setPendingFile(null);
  }, []);

  const handleNavigateToCompare = useCallback(() => {
    navigate('/compare');
  }, [navigate]);

  // Memoize loading states and computed values
  const showVideoSkeleton = useMemo(() =>
    !frameOverlay?.videoSrc && !isProcessing && !currentVideoId,
    [frameOverlay?.videoSrc, isProcessing, currentVideoId]
  );

  const showProcessing = useMemo(() =>
    isProcessing || isUploading,
    [isProcessing, isUploading]
  );

  const showMetricsSkeleton = useMemo(() =>
    metricsLoading || (isProcessing && progress < 75),
    [metricsLoading, isProcessing, progress]
  );

  const showFeedbackSkeleton = useMemo(() =>
    metricsLoading || (isProcessing && progress < 85),
    [metricsLoading, isProcessing, progress]
  );

  const hasMetrics = useMemo(() =>
    metrics && Object.keys(metrics).length > 0 && metrics.frame_indices?.length > 0,
    [metrics]
  );

  // Memoize chart series to prevent recreation
  const chartSeries = useMemo(() => {
    if (!metrics) return null;
    return {
      elbow: [
        { label: "Left", values: metrics.joint_angles?.elbow_left ?? [] },
        { label: "Right", values: metrics.joint_angles?.elbow_right ?? [] }
      ],
      shoulder: [
        { label: "Left", values: metrics.joint_angles?.shoulder_left ?? [] },
        { label: "Right", values: metrics.joint_angles?.shoulder_right ?? [] }
      ],
      bodyRoll: [{ label: "Roll", values: metrics.body_roll ?? [] }],
      handVelocities: [
        { label: "Left Hand", values: metrics.velocities?.hand_left ?? [] },
        { label: "Right Hand", values: metrics.velocities?.hand_right ?? [] }
      ],
      kickTiming: [{ label: "Left Ankle", values: metrics.kick_timing ?? [] }],
      bodyAlignment: [{ label: "Alignment", values: metrics.body_alignment ?? [] }]
    };
  }, [metrics]);

  // Refetch metrics when processing completes
  useEffect(() => {
    if (progress >= 100 && currentVideoId) {
      // Small delay to ensure backend has finished writing
      const timer = setTimeout(() => {
        refetchMetrics();
        refetchKeypoints(); // Also refetch keypoints
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [progress, currentVideoId, refetchMetrics, refetchKeypoints]);

  // Real-time keypoint updates during processing
  useEffect(() => {
    if (isProcessing && currentVideoId && progress > 10 && progress < 100) {
      // Refetch keypoints every 2 seconds while processing
      const interval = setInterval(() => {
        console.log('[DashboardPage] Refetching keypoints during processing...');
        refetchKeypoints();
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [isProcessing, currentVideoId, progress, refetchKeypoints]);

  return (
    <>
      {/* Video Trimmer Modal */}
      {showTrimmer && pendingFile && (
        <div className="trimmer-overlay">
          <Suspense fallback={<div style={{ padding: "20px", textAlign: "center" }}>Loading video trimmer...</div>}>
            <VideoTrimmer
              videoFile={pendingFile}
              onConfirm={handleTrimConfirm}
              onCancel={handleTrimCancel}
              maxDuration={300}
            />
          </Suspense>
        </div>
      )}

      {/* Show Test Layout if enabled */}
      {showTestLayout ? (
        <TestLayout />
      ) : (
        <div className="dashboard-grid">
          <section className="panel video-panel">
            <div className="upload-bar">
              <label className="upload-label" style={{ opacity: isUploading ? 0.6 : 1, pointerEvents: isUploading ? "none" : "auto" }}>
                <span>{isUploading ? "Uploading..." : "Upload Swim Video"}</span>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </label>

              {/* View Toggle Buttons */}
              <div style={{ marginLeft: "16px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
                {/* Test Layout Toggle */}
                <label style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  cursor: "pointer",
                  padding: "8px 12px",
                  backgroundColor: showTestLayout ? "#f59e0b" : "#1e293b",
                  borderRadius: "8px",
                  border: "2px solid #f59e0b"
                }}>
                  <input
                    type="checkbox"
                    checked={showTestLayout}
                    onChange={(e) => setShowTestLayout(e.target.checked)}
                    style={{ cursor: "pointer" }}
                  />
                  <span style={{ fontSize: "14px", color: "#e2e8f0", fontWeight: showTestLayout ? "600" : "normal" }}>
                    🧪 Test Layout
                  </span>
                </label>

                {/* Compare Videos Button */}
                <button
                  onClick={handleNavigateToCompare}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                    padding: "8px 16px",
                    backgroundColor: "#10b981",
                    border: "2px solid #059669",
                    borderRadius: "8px",
                    color: "#ffffff",
                    fontSize: "14px",
                    fontWeight: "600",
                    transition: "all 0.2s"
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = "#059669"}
                  onMouseLeave={(e) => e.target.style.backgroundColor = "#10b981"}
                >
                  ⚖️ Compare Videos
                </button>

                {/* Show current view indicator */}
                {frameOverlay?.videoSrc && !showTestLayout && (
                  <span style={{
                    fontSize: "14px",
                    color: "#94a3b8",
                    padding: "8px 12px",
                    backgroundColor: "#1e293b",
                    borderRadius: "8px",
                    border: "1px solid #334155"
                  }}>
                    🔬 3-Panel View Active
                  </span>
                )}

              </div>
              {uploadError && (
                <div style={{
                  marginTop: "10px",
                  padding: "10px",
                  backgroundColor: "#fee",
                  color: "#c33",
                  borderRadius: "4px",
                  fontSize: "14px"
                }}>
                  <strong>Upload Error:</strong> {uploadError}
                  <button
                    onClick={clearError}
                    style={{
                      marginLeft: "10px",
                      padding: "2px 8px",
                      cursor: "pointer",
                      backgroundColor: "#c33",
                      color: "white",
                      border: "none",
                      borderRadius: "3px"
                    }}
                  >
                    ×
                  </button>
                </div>
              )}
            </div>

            {showProcessing && (
              <ProcessingProgress
                stage={stage}
                progress={progress}
                message={message}
              />
            )}

            {showVideoSkeleton ? (
              <VideoSkeleton />
            ) : useAdvancedView && frameOverlay?.videoSrc ? (
              <>
                <div style={{ width: "100%", marginTop: "1rem" }}>
                  <ErrorBoundary name="SwimAnalysis" title="Swim Analysis Error" showRetry>
                    <SwimAnalysis
                      videoSrc={frameOverlay.videoSrc}
                      keypointsData={formattedKeypoints}
                      fps={frameOverlay.frameRate || 30}
                      trimStart={trimSettings.startTime}
                      trimEnd={trimSettings.endTime}
                      videoId={currentVideoId}
                    />
                  </ErrorBoundary>
                </div>

                {/* Metrics and Feedback Sections */}
                <section className="panel metrics-panel">
                  {showMetricsSkeleton ? (
                    <>
                      <MetricsSummarySkeleton />
                      <div className="metrics-charts">
                        <ChartSkeleton />
                        <ChartSkeleton />
                        <ChartSkeleton />
                      </div>
                    </>
                  ) : (
                    <ErrorBoundary name="Metrics" title="Metrics Error" showRetry>
                      <MetricsSummary metrics={metrics} />
                      <div className="metrics-charts">
                        {chartSeries && (
                          <>
                            <MetricsChart
                              title="Elbow Joint Angles"
                              series={chartSeries.elbow}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Angle (degrees)"
                            />
                            <MetricsChart
                              title="Shoulder Joint Angles"
                              series={chartSeries.shoulder}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Angle (degrees)"
                            />
                            <MetricsChart
                              title="Body Roll"
                              series={chartSeries.bodyRoll}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Roll (degrees)"
                            />
                            <MetricsChart
                              title="Hand Velocities"
                              series={chartSeries.handVelocities}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Velocity"
                            />
                            <MetricsChart
                              title="Kick Timing"
                              series={chartSeries.kickTiming}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Velocity"
                            />
                            <MetricsChart
                              title="Body Alignment"
                              series={chartSeries.bodyAlignment}
                              xAxis={metrics.frame_indices ?? []}
                              yAxisLabel="Angle (degrees)"
                            />
                          </>
                        )}
                      </div>
                    </ErrorBoundary>
                  )}
                </section>

                <section className="panel feedback-panel-wrapper">
                  {showFeedbackSkeleton ? (
                    <FeedbackSkeleton />
                  ) : (
                    <ErrorBoundary name="Feedback" title="Feedback Error" showRetry>
                      <FeedbackPanel
                        summary={narrative?.summary}
                        phaseBreakdown={narrative?.phase_breakdown}
                        keyMetrics={narrative?.key_metrics}
                        coaching={narrative?.coaching}
                      />
                      <ReportExport videoId={currentVideoId} onExport={() => { }} />
                    </ErrorBoundary>
                  )}
                </section>
              </>
            ) : (
              <div style={{ padding: "40px", textAlign: "center", color: "#94a3b8" }}>
                <p>Upload a video to see the 3-panel analysis view</p>
                <p style={{ fontSize: "12px", marginTop: "8px" }}>
                  Or use "Test Layout" to see the layout structure
                </p>
              </div>
            )}
          </section>

        </div>
      )}
    </>
  );
}

export default DashboardPage;
