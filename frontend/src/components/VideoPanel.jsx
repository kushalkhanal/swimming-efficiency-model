import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import PropTypes from "prop-types";

/**
 * Panel 1: Original video playback (no overlays)
 */
const VideoPanel = forwardRef(function VideoPanel(
  { videoSrc, trimStart = 0, trimEnd = null },
  ref
) {
  const videoRef = useRef(null);

  useImperativeHandle(ref, () => ({
    getVideoElement: () => videoRef.current,
    play: () => videoRef.current?.play(),
    pause: () => videoRef.current?.pause(),
    seekTo: (time) => {
      if (videoRef.current) {
        videoRef.current.currentTime = time;
      }
    },
  }));

  // Initialize video position
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !videoSrc) return;

    const handleLoadedMetadata = () => {
      video.currentTime = trimStart;
    };

    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    
    if (video.readyState >= 1) {
      video.currentTime = trimStart;
    }

    return () => {
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, [videoSrc, trimStart]);

  // Enforce trim boundaries
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      if (video.currentTime < trimStart) {
        video.currentTime = trimStart;
      }
      if (trimEnd && video.currentTime >= trimEnd) {
        video.currentTime = trimStart;
        video.pause();
      }
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
    };
  }, [trimStart, trimEnd]);

  if (!videoSrc) {
    return (
      <div className="panel-placeholder">
        No video loaded
      </div>
    );
  }

  return (
    <video
      ref={videoRef}
      src={videoSrc}
      className="video-player-element"
      playsInline
    />
  );
});

VideoPanel.propTypes = {
  videoSrc: PropTypes.string,
  trimStart: PropTypes.number,
  trimEnd: PropTypes.number,
};

export default VideoPanel;

