import { useState, useEffect } from "react";
import VideoPlayer from "../components/VideoPlayer";
import FrameNavigator from "../components/FrameNavigator";
import MetricsChart from "../components/MetricsChart";
import FeedbackPanel from "../components/FeedbackPanel";
import MetricsSummary from "../components/MetricsSummary";
import ReportExport from "../components/ReportExport";
import VideoTrimmer from "../components/VideoTrimmer";
import ErrorBoundary from "../components/ErrorBoundary";
import PoseViewer3D from "../components/PoseViewer3D";
import {
  VideoSkeleton,
  ChartSkeleton,
  MetricsSummarySkeleton,
  FeedbackSkeleton,
  ProcessingProgress,
} from "../components/Skeleton";
import { useVideoMetrics } from "../hooks/useVideoMetrics";
import { useFrameData } from "../hooks/useFrameData";
import { useProcessingProgress } from "../hooks/useProcessingProgress";
import { useKeypoints } from "../hooks/useKeypoints";

import "./DashboardPage.css";

function DashboardPage() {
  const [currentVideoId, setCurrentVideoId] = useState("");
  const [currentFrame, setCurrentFrame] = useState(0);
  const [showTrimmer, setShowTrimmer] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const [show3DViewer, setShow3DViewer] = useState(false);

  const { metrics, narrative, isLoading: metricsLoading, refetch: refetchMetrics } = useVideoMetrics(currentVideoId);
  const { frameOverlay, totalFrames, uploadVideo, exportReport, uploadError, isUploading, clearError } = useFrameData(
    currentVideoId
  );
  const { 
    stage, 
    progress, 
    message, 
    isProcessing, 
    startProcessing, 
    setUploadProgress,
    resetProgress 
  } = useProcessingProgress();
  const { currentKeypoints, setFrameIndex: setKeypointsFrame } = useKeypoints(currentVideoId);

  // Sync keypoints with current frame
  useEffect(() => {
    if (currentFrame && currentVideoId) {
      setKeypointsFrame(currentFrame);
    }
  }, [currentFrame, currentVideoId, setKeypointsFrame]);

  // Refetch metrics when processing completes
  useEffect(() => {
    if (progress >= 100 && currentVideoId) {
      // Small delay to ensure backend has finished writing
      const timer = setTimeout(() => {
        refetchMetrics();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [progress, currentVideoId, refetchMetrics]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      clearError();
      setPendingFile(file);
      setShowTrimmer(true);
    }
    // Reset input to allow uploading same file again
    event.target.value = "";
  };

  const handleTrimConfirm = (trimSettings) => {
    setShowTrimmer(false);
    if (pendingFile) {
      startProcessing(null);
      uploadVideo(pendingFile, setCurrentVideoId, setUploadProgress, trimSettings);
      setPendingFile(null);
    }
  };

  const handleTrimCancel = () => {
    setShowTrimmer(false);
    setPendingFile(null);
  };

  // Determine loading states
  const showVideoSkeleton = !frameOverlay?.videoSrc && !isProcessing && !currentVideoId;
  const showProcessing = isProcessing || isUploading;
  const showMetricsSkeleton = metricsLoading || (isProcessing && progress < 75);
  const showFeedbackSkeleton = metricsLoading || (isProcessing && progress < 85);
  const hasMetrics = metrics && Object.keys(metrics).length > 0 && metrics.frame_indices?.length > 0;

  return (
    <>
      {/* Video Trimmer Modal */}
      {showTrimmer && pendingFile && (
        <div className="trimmer-overlay">
          <VideoTrimmer
            videoFile={pendingFile}
            onConfirm={handleTrimConfirm}
            onCancel={handleTrimCancel}
            maxDuration={300}
          />
        </div>
      )}

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
        ) : (
          <ErrorBoundary name="VideoPlayer" title="Video Player Error" showRetry>
            {/* Side-by-side layout: Video + Pose */}
            <div className="video-pose-container">
              {/* Left: Video with 2D pose overlay */}
              <div className="video-side">
                <VideoPlayer
                  videoSrc={frameOverlay?.videoSrc}
                  overlay={frameOverlay}
                  keypoints={currentKeypoints}
                  onFrameChange={setCurrentFrame}
                />
              </div>
              
              {/* Right: 3D Pose viewer (optional, toggle) */}
              <div className="pose-side">
                <div className="pose-header">
                  <span>3D Pose View</span>
                  <button
                    className={`toggle-3d ${show3DViewer ? "active" : ""}`}
                    onClick={() => setShow3DViewer(!show3DViewer)}
                  >
                    {show3DViewer ? "Hide" : "Show"}
                  </button>
                </div>
                {show3DViewer && (
                  <PoseViewer3D
                    keypoints3d={currentKeypoints}
                    isPlaying={false}
                  />
                )}
                {!show3DViewer && (
                  <div className="pose-placeholder">
                    <span>🦴</span>
                    <p>Click "Show" to view 3D skeleton</p>
                  </div>
                )}
              </div>
            </div>
            
            <FrameNavigator
              currentFrame={currentFrame}
              totalFrames={totalFrames}
              onSeek={setCurrentFrame}
            />
          </ErrorBoundary>
        )}
      </section>

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
              <MetricsChart
                title="Elbow Joint Angles"
                series={[
                  { label: "Left", values: metrics.joint_angles?.elbow_left ?? [] },
                  { label: "Right", values: metrics.joint_angles?.elbow_right ?? [] }
                ]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Angle (degrees)"
              />
              <MetricsChart
                title="Shoulder Joint Angles"
                series={[
                  { label: "Left", values: metrics.joint_angles?.shoulder_left ?? [] },
                  { label: "Right", values: metrics.joint_angles?.shoulder_right ?? [] }
                ]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Angle (degrees)"
              />
              <MetricsChart
                title="Body Roll"
                series={[{ label: "Roll", values: metrics.body_roll ?? [] }]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Roll (degrees)"
              />
              <MetricsChart
                title="Hand Velocities"
                series={[
                  { label: "Left Hand", values: metrics.velocities?.hand_left ?? [] },
                  { label: "Right Hand", values: metrics.velocities?.hand_right ?? [] }
                ]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Velocity"
              />
              <MetricsChart
                title="Kick Timing"
                series={[{ label: "Left Ankle", values: metrics.kick_timing ?? [] }]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Velocity"
              />
              <MetricsChart
                title="Body Alignment"
                series={[{ label: "Alignment", values: metrics.body_alignment ?? [] }]}
                xAxis={metrics.frame_indices ?? []}
                yAxisLabel="Angle (degrees)"
              />
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
            <ReportExport videoId={currentVideoId} onExport={exportReport} />
          </ErrorBoundary>
        )}
      </section>
    </div>
    </>
  );
}

export default DashboardPage;
