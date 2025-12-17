import { useEffect, useRef } from "react";
import PropTypes from "prop-types";

import "./VideoPlayer.css";

// MediaPipe pose connections for skeleton drawing
const POSE_CONNECTIONS = [
  // Torso
  [11, 12], // shoulders
  [11, 23], // left shoulder to hip
  [12, 24], // right shoulder to hip
  [23, 24], // hips
  // Left arm
  [11, 13], // shoulder to elbow
  [13, 15], // elbow to wrist
  // Right arm
  [12, 14], // shoulder to elbow
  [14, 16], // elbow to wrist
  // Left leg
  [23, 25], // hip to knee
  [25, 27], // knee to ankle
  // Right leg
  [24, 26], // hip to knee
  [26, 28], // knee to ankle
  // Face
  [0, 11], // nose to left shoulder
  [0, 12], // nose to right shoulder
];

// Color scheme for body parts
const getJointColor = (index) => {
  if (index <= 10) return "#f59e0b"; // Face - amber
  if (index >= 11 && index <= 16) return "#3b82f6"; // Arms - blue
  if (index >= 17 && index <= 22) return "#8b5cf6"; // Hands - purple
  if (index >= 23 && index <= 28) return "#10b981"; // Legs - green
  return "#94a3b8"; // Default
};

const getBoneColor = (startIdx, endIdx) => {
  if ([11, 13, 15].includes(startIdx) || [12, 14, 16].includes(startIdx)) return "#3b82f6"; // Arms
  if ([23, 25, 27].includes(startIdx) || [24, 26, 28].includes(startIdx)) return "#10b981"; // Legs
  return "#e2e8f0"; // Torso
};

/**
 * Renders the swimmer video with a 2D pose skeleton overlay.
 */
function VideoPlayer({ videoSrc = null, overlay = null, keypoints = null, onFrameChange = () => {} }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const resizeCanvas = () => {
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 360;
    };

    if (video.readyState >= 1) {
      resizeCanvas();
    } else {
      video.addEventListener("loadedmetadata", resizeCanvas, { once: true });
    }

    const handleTimeUpdate = () => {
      const frameRate = overlay?.frameRate || 30;
      const currentFrame = Math.floor(video.currentTime * frameRate);
      onFrameChange?.(currentFrame);
    };

    video.addEventListener("timeupdate", handleTimeUpdate);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
    };
  }, [overlay, onFrameChange]);

  // Draw pose overlay when keypoints change
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw keypoints if available
    if (keypoints && keypoints.length > 0) {
      const w = canvas.width;
      const h = canvas.height;
      
      // Draw bones first (so joints appear on top)
      ctx.lineWidth = 3;
      POSE_CONNECTIONS.forEach(([startIdx, endIdx]) => {
        const start = keypoints[startIdx];
        const end = keypoints[endIdx];
        
        if (start && end && start.length >= 2 && end.length >= 2) {
          // Check if points are valid (not zero)
          if (start[0] === 0 && start[1] === 0) return;
          if (end[0] === 0 && end[1] === 0) return;
          
          ctx.strokeStyle = getBoneColor(startIdx, endIdx);
          ctx.beginPath();
          ctx.moveTo(start[0] * w, start[1] * h);
          ctx.lineTo(end[0] * w, end[1] * h);
          ctx.stroke();
        }
      });
      
      // Draw joints
      keypoints.slice(0, 29).forEach((kp, idx) => {
        if (kp && kp.length >= 2 && (kp[0] !== 0 || kp[1] !== 0)) {
          const x = kp[0] * w;
          const y = kp[1] * h;
          const radius = idx === 0 ? 8 : 5; // Larger for head
          
          ctx.fillStyle = getJointColor(idx);
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, 2 * Math.PI);
          ctx.fill();
          
          // White border for visibility
          ctx.strokeStyle = "white";
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }
      });
    } else if (overlay?.keypoints) {
      // Fallback to old overlay format
      ctx.fillStyle = "#38bdf8";
      overlay.keypoints.forEach(([x, y]) => {
        ctx.beginPath();
        ctx.arc(x * canvas.width, y * canvas.height, 4, 0, 2 * Math.PI);
        ctx.fill();
      });
    }
  }, [keypoints, overlay]);

  return (
    <div className="video-player">
      <video ref={videoRef} src={videoSrc} controls />
      <canvas ref={canvasRef} />
    </div>
  );
}

VideoPlayer.propTypes = {
  videoSrc: PropTypes.string,
  overlay: PropTypes.shape({
    frameRate: PropTypes.number,
    keypoints: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number))
  }),
  keypoints: PropTypes.array,
  onFrameChange: PropTypes.func
};

export default VideoPlayer;

