import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { draw2DOverlay } from "../utils/draw2D";
import BiomechLegend from "./BiomechLegend";
import axios from "axios";

/**
 * Panel 2: 2D skeleton overlay on video frame
 * Draws video frame with colored skeleton overlay synchronized with video playback.
 */
function Skeleton2DPanel({ videoRef, keypoints, currentFrame, showSkeleton = true, videoId }) {
  const canvasRef = useRef(null);
  const [canvasSize, setCanvasSize] = useState({ width: 640, height: 480 });
  const [frameRatings, setFrameRatings] = useState({});

  // Fetch frame analytics for current frame
  useEffect(() => {
    if (!videoId || currentFrame === undefined) return;

    const fetchFrameAnalytics = async () => {
      try {
        const response = await axios.get(
          `/api/v1/frame-analytics/${videoId}/${currentFrame}`
        );
        if (response.data && response.data.ratings) {
          setFrameRatings(response.data.ratings);
        }
      } catch (error) {
        // Silently fail - ratings are optional enhancement
        console.debug('Frame analytics not available:', error.message);
        setFrameRatings({});
      }
    };

    fetchFrameAnalytics();
  }, [videoId, currentFrame]);

  // Update canvas size based on video dimensions
  useEffect(() => {
    const canvas = canvasRef.current;

    // Get video element from ref (handle VideoPanel's useImperativeHandle)
    let video = null;
    if (videoRef) {
      if (videoRef.current && typeof videoRef.current.getVideoElement === 'function') {
        video = videoRef.current.getVideoElement();
      } else if (videoRef.current instanceof HTMLVideoElement) {
        video = videoRef.current;
      } else if (typeof videoRef.getVideoElement === 'function') {
        video = videoRef.getVideoElement();
      } else if (videoRef instanceof HTMLVideoElement) {
        video = videoRef;
      }
    }

    if (!canvas) return;

    const updateCanvasSize = () => {
      if (video && video.videoWidth > 0 && video.videoHeight > 0) {
        // Set canvas to match video's intrinsic dimensions
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        setCanvasSize({ width: video.videoWidth, height: video.videoHeight });
      } else {
        // Fallback: use container size
        const container = canvas.parentElement;
        if (container) {
          const width = container.clientWidth || 640;
          const height = container.clientHeight || 480;
          canvas.width = width;
          canvas.height = height;
          setCanvasSize({ width, height });
        }
      }

      // Don't set CSS dimensions - let object-fit: contain handle the scaling
      // The CSS in SwimAnalysis.css handles this with width: 100%, height: 100%, object-fit: contain
    };

    if (video) {
      if (video.readyState >= 2) {
        updateCanvasSize();
      } else {
        video.addEventListener('loadedmetadata', updateCanvasSize, { once: true });
      }
    } else {
      updateCanvasSize();
    }

    window.addEventListener("resize", updateCanvasSize);
    return () => {
      window.removeEventListener("resize", updateCanvasSize);
      if (video) {
        video.removeEventListener('loadedmetadata', updateCanvasSize);
      }
    };
  }, [videoRef]);

  // Draw skeleton overlay synchronized with video frame
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    // Get video element from ref (handle VideoPanel's useImperativeHandle)
    let video = null;
    if (videoRef) {
      // videoRef is the ref object from SwimAnalysis (videoRef from useRef)
      // VideoPanel exposes getVideoElement() via useImperativeHandle on videoRef.current
      if (videoRef.current && typeof videoRef.current.getVideoElement === 'function') {
        video = videoRef.current.getVideoElement();
      } else if (videoRef.current instanceof HTMLVideoElement) {
        video = videoRef.current;
      } else if (typeof videoRef.getVideoElement === 'function') {
        video = videoRef.getVideoElement();
      } else if (videoRef instanceof HTMLVideoElement) {
        video = videoRef;
      }
    }

    const draw = () => {
      if (!showSkeleton) {
        // If skeleton is hidden, just draw video frame
        if (video && video.readyState >= 2) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          try {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          } catch (error) {
            // Video not ready
          }
        } else {
          // Draw dark background
          ctx.fillStyle = '#0F172A';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        return;
      }

      // Draw video frame with skeleton overlay
      draw2DOverlay(ctx, video, keypoints, canvas.width, canvas.height, frameRatings);
    };

    // Draw immediately
    draw();

    // Use requestAnimationFrame for smooth updates during playback
    let animationFrameId;
    const update = () => {
      draw();
      if (video && !video.paused && !video.ended) {
        animationFrameId = requestAnimationFrame(update);
      }
    };

    // Start animation loop if video is playing
    if (video && !video.paused && !video.ended) {
      animationFrameId = requestAnimationFrame(update);
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [currentFrame, keypoints, showSkeleton, videoRef, canvasSize, frameRatings]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <canvas
        ref={canvasRef}
        className="skeleton-2d-canvas"
        style={{
          display: 'block',
          width: '100%',
          height: 'auto',
          maxWidth: '100%',
          maxHeight: '100%',
        }}
      />
      <BiomechLegend show={showSkeleton} />
    </div>
  );
}

Skeleton2DPanel.propTypes = {
  videoRef: PropTypes.oneOfType([
    PropTypes.shape({
      current: PropTypes.object,
      getVideoElement: PropTypes.func,
    }),
    PropTypes.object, // Can be direct video ref object
  ]),
  keypoints: PropTypes.object, // { jointName: { x, y, z, confidence } }
  currentFrame: PropTypes.number.isRequired,
  showSkeleton: PropTypes.bool,
  videoId: PropTypes.string, // Video ID for fetching frame analytics
};

export default Skeleton2DPanel;

