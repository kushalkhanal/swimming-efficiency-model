import { useState } from "react";
import "./TestLayout.css";

/**
 * Test layout component to visually verify 3-panel structure.
 * Shows colored borders for easy identification of each panel.
 */
function TestLayout() {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [show2D, setShow2D] = useState(true);
  const [show3D, setShow3D] = useState(true);

  const totalFrames = 300;

  const handlePrevFrame = () => {
    setIsPlaying(false);
    setCurrentFrame((prev) => Math.max(0, prev - 1));
  };

  const handleNextFrame = () => {
    setIsPlaying(false);
    setCurrentFrame((prev) => Math.min(totalFrames, prev + 1));
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSpeedChange = (speed) => {
    setPlaybackSpeed(speed);
  };

  const handleScrub = (frame) => {
    setIsPlaying(false);
    setCurrentFrame(frame);
  };

  return (
    <div className="test-layout-container">
      <div className="test-panels-container">
        {/* Panel 1: Original Video (Orange Border) */}
        <div className="test-panel test-panel-video">
          <div className="test-panel-header">
            <span>📹 Original Video</span>
          </div>
          <div className="test-panel-content">
            <div className="test-placeholder test-video-placeholder">
              <div className="test-placeholder-text">[VIDEO PLAYING]</div>
              <div className="test-placeholder-info">Orange Border</div>
            </div>
          </div>
        </div>

        {/* Panel 2: 2D Skeleton Overlay (Blue Border) */}
        {show2D && (
          <div className="test-panel test-panel-2d">
            <div className="test-panel-header">
              <span>🦴 2D Skeleton Overlay</span>
              <button
                className="test-panel-toggle-btn"
                onClick={() => setShow2D(false)}
                aria-label="Hide 2D view"
              >
                ✕
              </button>
            </div>
            <div className="test-panel-content">
              <div className="test-placeholder test-canvas-placeholder">
                <div className="test-placeholder-text">[2D CANVAS]</div>
                <div className="test-placeholder-info">(placeholder)</div>
                <div className="test-placeholder-info">Blue Border</div>
              </div>
            </div>
          </div>
        )}

        {/* Panel 3: 3D Pose Viewer (Green Border) */}
        {show3D && (
          <div className="test-panel test-panel-3d">
            <div className="test-panel-header">
              <span>🎯 3D Pose Viewer</span>
              <button
                className="test-panel-toggle-btn"
                onClick={() => setShow3D(false)}
                aria-label="Hide 3D view"
              >
                ✕
              </button>
            </div>
            <div className="test-panel-content">
              <div className="test-placeholder test-3d-placeholder">
                <div className="test-placeholder-text">[3D VIEWER]</div>
                <div className="test-placeholder-info">(placeholder)</div>
                <div className="test-placeholder-info">Green Border</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="test-control-bar">
        {/* Playback Controls */}
        <div className="test-control-group">
          <button onClick={handlePrevFrame} className="test-control-btn">
            ⏮️ Prev
          </button>
          <button
            onClick={handlePlayPause}
            className={`test-control-btn ${isPlaying ? "active" : ""}`}
          >
            {isPlaying ? "⏸️ Pause" : "▶️ Play"}
          </button>
          <button onClick={handleNextFrame} className="test-control-btn">
            ⏭️ Next
          </button>
        </div>

        {/* Speed Control */}
        <div className="test-control-group">
          <label className="test-control-label">Speed:</label>
          <div className="test-speed-buttons">
            {[0.25, 0.5, 1, 1.5, 2].map((speed) => (
              <button
                key={speed}
                onClick={() => handleSpeedChange(speed)}
                className={`test-control-btn ${playbackSpeed === speed ? "active" : ""}`}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>

        {/* Timeline Scrubber */}
        <div className="test-control-group test-timeline">
          <input
            type="range"
            min="0"
            max={totalFrames}
            value={currentFrame}
            onChange={(e) => handleScrub(parseInt(e.target.value))}
            className="test-timeline-slider"
          />
          <span className="test-frame-counter">
            Frame: {currentFrame} / {totalFrames}
          </span>
        </div>

        {/* Panel Toggles */}
        <div className="test-control-group">
          <label className="test-toggle-label">
            <input
              type="checkbox"
              checked={show2D}
              onChange={(e) => setShow2D(e.target.checked)}
            />
            <span>2D Skeleton</span>
          </label>
          <label className="test-toggle-label">
            <input
              type="checkbox"
              checked={show3D}
              onChange={(e) => setShow3D(e.target.checked)}
            />
            <span>3D View</span>
          </label>
        </div>
      </div>
    </div>
  );
}

export default TestLayout;

