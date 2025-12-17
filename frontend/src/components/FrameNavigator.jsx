import PropTypes from "prop-types";
import "./FrameNavigator.css";

/**
 * Provides frame-by-frame navigation controls synced with the video player.
 */
function FrameNavigator({ currentFrame = 0, totalFrames = 0, onSeek = () => {} }) {
  return (
    <div className="frame-navigator">
      <button onClick={() => onSeek(Math.max(currentFrame - 1, 0))}>Prev</button>
      <div>
        Frame {currentFrame} / {totalFrames}
      </div>
      <button onClick={() => onSeek(Math.min(currentFrame + 1, totalFrames))}>
        Next
      </button>
    </div>
  );
}

FrameNavigator.propTypes = {
  currentFrame: PropTypes.number,
  totalFrames: PropTypes.number,
  onSeek: PropTypes.func
};

export default FrameNavigator;

