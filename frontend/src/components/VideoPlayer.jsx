import { useEffect, useRef, useImperativeHandle, forwardRef, useState, useCallback } from "react";
import PropTypes from "prop-types";

import "./VideoPlayer.css";

/**
 * Renders the swimmer video with trim boundaries.
 * Video plays only within the trimmed segment.
 */
const VideoPlayer = forwardRef(function VideoPlayer(
  { 
    videoSrc = null, 
    overlay = null, 
    trimStart = 0, 
    trimEnd = null,
    onFrameChange = () => {},
    onTimeUpdate = () => {},
  },
  ref
) {
  const videoRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Calculate trimmed duration
  const trimmedDuration = trimEnd ? trimEnd - trimStart : 0;

  // Expose video element and controls to parent
  useImperativeHandle(ref, () => ({
    getVideoElement: () => videoRef.current,
    seekTo: (time) => {
      if (videoRef.current) {
        videoRef.current.currentTime = trimStart + time;
      }
    },
    play: () => videoRef.current?.play(),
    pause: () => videoRef.current?.pause(),
  }));

  // Set initial position when video loads
  useEffect(() => {
    if (!videoRef.current || !videoSrc) return;

    const video = videoRef.current;

    const handleLoadedMetadata = () => {
      // Set to trim start position
      video.currentTime = trimStart;
      setIsReady(true);
    };

    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    
    // If already loaded, set position
    if (video.readyState >= 1) {
      video.currentTime = trimStart;
      setIsReady(true);
    }

    return () => {
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, [videoSrc, trimStart]);

  // Handle time updates and enforce trim boundaries
  useEffect(() => {
    if (!videoRef.current) return;

    const video = videoRef.current;

    const handleTimeUpdate = () => {
      const absoluteTime = video.currentTime;
      
      // Enforce trim boundaries
      if (absoluteTime < trimStart) {
        video.currentTime = trimStart;
        return;
      }
      
      if (trimEnd && absoluteTime >= trimEnd) {
        video.currentTime = trimStart;
        video.pause();
        setIsPlaying(false);
        return;
      }

      // Calculate relative time within trim
      const relativeTime = absoluteTime - trimStart;
      setCurrentTime(relativeTime);
      
      // Calculate frame number relative to trim start
      const frameRate = overlay?.frameRate || 30;
      const currentFrame = Math.floor(relativeTime * frameRate);
      onFrameChange?.(currentFrame);
      onTimeUpdate?.(relativeTime, trimmedDuration);
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleSeeking = () => {
      // Prevent seeking outside trim boundaries
      if (video.currentTime < trimStart) {
        video.currentTime = trimStart;
      } else if (trimEnd && video.currentTime > trimEnd) {
        video.currentTime = trimEnd - 0.1;
      }
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("play", handlePlay);
    video.addEventListener("pause", handlePause);
    video.addEventListener("seeking", handleSeeking);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("play", handlePlay);
      video.removeEventListener("pause", handlePause);
      video.removeEventListener("seeking", handleSeeking);
    };
  }, [overlay, trimStart, trimEnd, trimmedDuration, onFrameChange, onTimeUpdate]);

  // Format time as M:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Handle custom scrubber
  const handleScrub = useCallback((e) => {
    if (!videoRef.current || !trimmedDuration) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const newTime = trimStart + (percent * trimmedDuration);
    videoRef.current.currentTime = newTime;
  }, [trimStart, trimmedDuration]);

  // Toggle play/pause
  const togglePlay = useCallback(() => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  }, [isPlaying]);

  return (
    <div className="video-player">
      <video 
        ref={videoRef} 
        src={videoSrc}
        onClick={togglePlay}
      />
      
      {/* Custom controls for trimmed playback */}
      {isReady && trimmedDuration > 0 && (
        <div className="video-controls">
          <button className="play-btn" onClick={togglePlay}>
            {isPlaying ? "⏸" : "▶"}
          </button>
          
          <div className="time-display">
            {formatTime(currentTime)} / {formatTime(trimmedDuration)}
          </div>
          
          <div className="scrubber" onClick={handleScrub}>
            <div 
              className="scrubber-progress" 
              style={{ width: `${(currentTime / trimmedDuration) * 100}%` }}
            />
            <div 
              className="scrubber-handle"
              style={{ left: `${(currentTime / trimmedDuration) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
});

VideoPlayer.propTypes = {
  videoSrc: PropTypes.string,
  overlay: PropTypes.shape({
    frameRate: PropTypes.number,
    keypoints: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number))
  }),
  trimStart: PropTypes.number,
  trimEnd: PropTypes.number,
  onFrameChange: PropTypes.func,
  onTimeUpdate: PropTypes.func,
};

export default VideoPlayer;

