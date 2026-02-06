import PropTypes from "prop-types";
import "./ControlBar.css";

/**
 * Unified control bar for all panels
 * Provides playback controls, speed control, timeline, and panel toggles
 */
function ControlBar({
  currentFrame,
  totalFrames,
  isPlaying,
  playbackSpeed,
  show2D,
  show3D,
  onPrevFrame,
  onNextFrame,
  onPlayPause,
  onSpeedChange,
  onScrub,
  onToggle2D,
  onToggle3D,
}) {
  const speedOptions = [0.25, 0.5, 1, 1.5, 2];

  return (
    <div className="control-bar">
      {/* Playback Controls */}
      <div className="control-group playback-controls">
        <button 
          onClick={onPrevFrame}
          className="control-btn"
          aria-label="Previous frame"
        >
          ⏮️ Prev
        </button>
        <button 
          onClick={onPlayPause}
          className={`control-btn ${isPlaying ? "active" : ""}`}
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? "⏸️ Pause" : "▶️ Play"}
        </button>
        <button 
          onClick={onNextFrame}
          className="control-btn"
          aria-label="Next frame"
        >
          ⏭️ Next
        </button>
      </div>

      {/* Speed Control */}
      <div className="control-group speed-control">
        <label className="control-label">Speed:</label>
        <div className="speed-buttons">
          {speedOptions.map((speed) => (
            <button
              key={speed}
              onClick={() => onSpeedChange(speed)}
              className={`control-btn ${playbackSpeed === speed ? "active" : ""}`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Scrubber */}
      <div className="control-group timeline">
        <input
          type="range"
          min="0"
          max={totalFrames}
          value={currentFrame}
          onChange={(e) => onScrub(parseInt(e.target.value))}
          className="timeline-slider"
          aria-label="Timeline scrubber"
        />
        <span className="frame-counter">
          Frame: {currentFrame} / {totalFrames}
        </span>
      </div>

      {/* Panel Toggles */}
      <div className="control-group panel-toggles">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={show2D}
            onChange={onToggle2D}
          />
          <span>2D Skeleton</span>
        </label>
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={show3D}
            onChange={onToggle3D}
          />
          <span>3D View</span>
        </label>
      </div>
    </div>
  );
}

ControlBar.propTypes = {
  currentFrame: PropTypes.number.isRequired,
  totalFrames: PropTypes.number.isRequired,
  isPlaying: PropTypes.bool.isRequired,
  playbackSpeed: PropTypes.number.isRequired,
  show2D: PropTypes.bool.isRequired,
  show3D: PropTypes.bool.isRequired,
  onPrevFrame: PropTypes.func.isRequired,
  onNextFrame: PropTypes.func.isRequired,
  onPlayPause: PropTypes.func.isRequired,
  onSpeedChange: PropTypes.func.isRequired,
  onScrub: PropTypes.func.isRequired,
  onToggle2D: PropTypes.func.isRequired,
  onToggle3D: PropTypes.func.isRequired,
};

export default ControlBar;

