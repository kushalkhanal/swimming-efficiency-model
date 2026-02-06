import { useState, useRef, useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import VideoPanel from "./VideoPanel";
import Skeleton2DPanel from "./Skeleton2DPanel";
import Pose3DPanel from "./Pose3DPanel";
import ControlBar from "./ControlBar";
import "./SwimAnalysis.css";

/**
 * Main container component for 3-panel swim analysis interface.
 * 
 * Features:
 * - Panel 1: Original video (left)
 * - Panel 2: 2D skeleton overlay (middle)
 * - Panel 3: 3D pose viewer (right)
 * - Unified control bar at bottom
 */
function SwimAnalysis({
  videoSrc,
  keypointsData = {},
  fps = 30,
  trimStart = 0,
  trimEnd = null,
  videoId = null
}) {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [show2D, setShow2D] = useState(true);
  const [show3D, setShow3D] = useState(true);

  const videoRef = useRef(null);

  // Calculate total frames
  const getVideoElementForCalc = () => {
    const ref = videoRef.current;
    if (!ref) return null;
    return ref.getVideoElement?.() || ref;
  };

  const videoForCalc = getVideoElementForCalc();
  const totalFrames = trimEnd
    ? Math.floor((trimEnd - trimStart) * fps)
    : videoForCalc
      ? Math.floor((videoForCalc.duration || 0) * fps)
      : 0;

  // Get video element helper
  const getVideoElement = () => {
    const ref = videoRef.current;
    if (!ref) return null;
    return ref.getVideoElement?.() || ref;
  };

  // Handle frame navigation
  const handlePrevFrame = () => {
    setIsPlaying(false);
    const video = getVideoElement();
    if (video) {
      const newTime = Math.max(trimStart, video.currentTime - 1 / fps);
      video.currentTime = newTime;
      setCurrentFrame(Math.floor((newTime - trimStart) * fps));
    }
  };

  const handleNextFrame = () => {
    setIsPlaying(false);
    const video = getVideoElement();
    if (video) {
      const maxTime = trimEnd || (video.duration || 0);
      const newTime = Math.min(maxTime, video.currentTime + 1 / fps);
      video.currentTime = newTime;
      setCurrentFrame(Math.floor((newTime - trimStart) * fps));
    }
  };

  const handlePlayPause = () => {
    const video = getVideoElement();
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSpeedChange = (speed) => {
    const video = getVideoElement();
    if (video) {
      video.playbackRate = speed;
      setPlaybackSpeed(speed);
    }
  };

  const handleScrub = (frame) => {
    setIsPlaying(false);
    const video = getVideoElement();
    if (video) {
      const time = trimStart + (frame / fps);
      video.currentTime = time;
      setCurrentFrame(frame);
    }
  };

  // Sync frame updates from video
  useEffect(() => {
    const video = getVideoElement();
    if (!video) return;

    const handleTimeUpdate = () => {
      const relativeTime = video.currentTime - trimStart;
      const frame = Math.floor(relativeTime * fps);
      setCurrentFrame(Math.max(0, frame));

      // Enforce trim boundaries
      if (trimEnd && video.currentTime >= trimEnd) {
        video.currentTime = trimStart;
        video.pause();
        setIsPlaying(false);
      }
      if (video.currentTime < trimStart) {
        video.currentTime = trimStart;
      }
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("play", handlePlay);
    video.addEventListener("pause", handlePause);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("play", handlePlay);
      video.removeEventListener("pause", handlePause);
    };
  }, [trimStart, trimEnd, fps]);

  // Get current frame keypoints
  // Keypoints are indexed by absolute frame numbers from the API
  // currentFrame is relative to trim start, so we need to convert to absolute frame number
  const currentKeypoints = useMemo(() => {
    if (!keypointsData || Object.keys(keypointsData).length === 0) {
      return null;
    }

    // Convert relative frame to absolute frame number
    // trimStart is in seconds, convert to frames
    const trimStartFrame = Math.floor(trimStart * fps);
    const absoluteFrame = trimStartFrame + currentFrame;

    // Try to get keypoints for the absolute frame
    let keypoints = keypointsData[absoluteFrame];

    // If not found exactly, try to find the closest frame
    if (!keypoints) {
      const frameKeys = Object.keys(keypointsData).map(Number).sort((a, b) => a - b);
      if (frameKeys.length > 0) {
        // Find the closest frame index
        const closestFrame = frameKeys.reduce((prev, curr) => {
          return Math.abs(curr - absoluteFrame) < Math.abs(prev - absoluteFrame) ? curr : prev;
        });
        // Only use if it's reasonably close (within 5 frames)
        if (Math.abs(closestFrame - absoluteFrame) <= 5) {
          keypoints = keypointsData[closestFrame];
        }
      }
    }

    return keypoints || null;
  }, [keypointsData, currentFrame, trimStart, fps]);

  return (
    <div className="swim-analysis-container">
      <div className="panels-container">
        {/* Panel 1: Original Video */}
        <div className="panel panel-video">
          <div className="panel-header">
            <span>📹 Original Video</span>
          </div>
          <div className="panel-content">
            <VideoPanel
              ref={videoRef}
              videoSrc={videoSrc}
              trimStart={trimStart}
              trimEnd={trimEnd}
            />
          </div>
        </div>

        {/* Panel 2: 2D Skeleton Overlay */}
        {show2D && (
          <div className="panel panel-2d">
            <div className="panel-header">
              <span>🦴 2D Skeleton Overlay</span>
              <button
                className="panel-toggle-btn"
                onClick={() => setShow2D(false)}
                aria-label="Hide 2D view"
              >
                ✕
              </button>
            </div>
            <div className="panel-content">
              <Skeleton2DPanel
                videoRef={videoRef}
                keypoints={currentKeypoints}
                currentFrame={currentFrame}
                showSkeleton={show2D}
                videoId={videoId}
              />
            </div>
          </div>
        )}

        {/* Panel 3: 3D Pose Viewer */}
        {show3D && (
          <div className="panel panel-3d">
            <div className="panel-header">
              <span>🎯 3D Pose Viewer</span>
              <button
                className="panel-toggle-btn"
                onClick={() => setShow3D(false)}
                aria-label="Hide 3D view"
              >
                ✕
              </button>
            </div>
            <div className="panel-content">
              <Pose3DPanel
                keypoints={currentKeypoints}
                currentFrame={currentFrame}
              />
            </div>
          </div>
        )}
      </div>

      {/* Unified Control Bar */}
      <ControlBar
        currentFrame={currentFrame}
        totalFrames={totalFrames}
        isPlaying={isPlaying}
        playbackSpeed={playbackSpeed}
        show2D={show2D}
        show3D={show3D}
        onPrevFrame={handlePrevFrame}
        onNextFrame={handleNextFrame}
        onPlayPause={handlePlayPause}
        onSpeedChange={handleSpeedChange}
        onScrub={handleScrub}
        onToggle2D={() => setShow2D(!show2D)}
        onToggle3D={() => setShow3D(!show3D)}
      />
    </div>
  );
}

SwimAnalysis.propTypes = {
  videoSrc: PropTypes.string,
  keypointsData: PropTypes.object, // { frameNumber: { keypointName: { x, y, z, confidence } } }
  fps: PropTypes.number,
  trimStart: PropTypes.number,
  trimEnd: PropTypes.number,
  videoId: PropTypes.string,
};

export default SwimAnalysis;

