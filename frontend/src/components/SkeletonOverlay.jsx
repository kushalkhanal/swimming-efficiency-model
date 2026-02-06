import { useEffect, useRef, useCallback } from "react";
import PropTypes from "prop-types";
import "./SkeletonOverlay.css";

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
  // Arms
  if ([11, 13, 15].includes(startIdx) && [13, 15].includes(endIdx)) return "#3b82f6";
  if ([12, 14, 16].includes(startIdx) && [14, 16].includes(endIdx)) return "#3b82f6";
  // Legs
  if ([23, 25, 27].includes(startIdx) && [25, 27].includes(endIdx)) return "#10b981";
  if ([24, 26, 28].includes(startIdx) && [26, 28].includes(endIdx)) return "#10b981";
  // Torso/face
  return "#e2e8f0";
};

/**
 * Synced 2D Skeleton Overlay Panel
 * Shows video frame with skeleton drawn on top, synced with main video player
 * Supports trimmed video playback with relative frame counting
 */
function SkeletonOverlay({ 
  videoRef, 
  keypoints, 
  currentFrame, 
  totalFrames,
  trimStart = 0,
  trimEnd = null,
  fps = 30,
}) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // Calculate trimmed frame info
  const trimStartFrame = Math.floor(trimStart * fps);
  const trimEndFrame = trimEnd ? Math.floor(trimEnd * fps) : totalFrames;
  const trimmedTotalFrames = trimEndFrame - trimStartFrame;
  
  // Current frame relative to trim (starts at 1)
  const relativeFrame = currentFrame + 1;

  // Draw the current video frame and skeleton overlay
  const drawFrame = useCallback(() => {
    const canvas = canvasRef.current;
    const video = videoRef?.current;
    
    if (!canvas || !video) return;
    
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, w, h);
    
    // Draw video frame if video is ready
    if (video.readyState >= 2 && video.videoWidth > 0) {
      // Calculate aspect ratio to fit video in canvas
      const videoAspect = video.videoWidth / video.videoHeight;
      const canvasAspect = w / h;
      
      let drawWidth, drawHeight, offsetX, offsetY;
      
      if (videoAspect > canvasAspect) {
        // Video is wider - fit to width
        drawWidth = w;
        drawHeight = w / videoAspect;
        offsetX = 0;
        offsetY = (h - drawHeight) / 2;
      } else {
        // Video is taller - fit to height
        drawHeight = h;
        drawWidth = h * videoAspect;
        offsetX = (w - drawWidth) / 2;
        offsetY = 0;
      }
      
      // Draw video frame
      ctx.drawImage(video, offsetX, offsetY, drawWidth, drawHeight);
      
      // Draw skeleton overlay if keypoints available
      if (keypoints && keypoints.length > 0) {
        // Draw bones first
        ctx.lineCap = "round";
        
        POSE_CONNECTIONS.forEach(([startIdx, endIdx]) => {
          const start = keypoints[startIdx];
          const end = keypoints[endIdx];
          
          if (start && end && start.length >= 2 && end.length >= 2) {
            // Skip invalid points
            if ((start[0] === 0 && start[1] === 0) || (end[0] === 0 && end[1] === 0)) return;
            
            const x1 = offsetX + start[0] * drawWidth;
            const y1 = offsetY + start[1] * drawHeight;
            const x2 = offsetX + end[0] * drawWidth;
            const y2 = offsetY + end[1] * drawHeight;
            
            // Draw bone shadow for visibility
            ctx.strokeStyle = "rgba(0, 0, 0, 0.6)";
            ctx.lineWidth = 8;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
            
            // Draw bone
            ctx.strokeStyle = getBoneColor(startIdx, endIdx);
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
          }
        });
        
        // Draw joints
        keypoints.slice(0, 29).forEach((kp, idx) => {
          if (kp && kp.length >= 2 && (kp[0] !== 0 || kp[1] !== 0)) {
            const x = offsetX + kp[0] * drawWidth;
            const y = offsetY + kp[1] * drawHeight;
            const radius = idx === 0 ? 12 : 8; // Larger for head
            
            // Draw shadow
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            ctx.beginPath();
            ctx.arc(x + 2, y + 2, radius, 0, 2 * Math.PI);
            ctx.fill();
            
            // Draw joint
            ctx.fillStyle = getJointColor(idx);
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, 2 * Math.PI);
            ctx.fill();
            
            // White border
            ctx.strokeStyle = "white";
            ctx.lineWidth = 2.5;
            ctx.stroke();
          }
        });
      } else {
        // No keypoints - show message
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        ctx.fillRect(w/2 - 100, h/2 - 15, 200, 30);
        ctx.fillStyle = "#94a3b8";
        ctx.font = "14px system-ui";
        ctx.textAlign = "center";
        ctx.fillText("No pose data for this frame", w / 2, h / 2 + 5);
      }
    } else {
      // Video not ready - show placeholder
      ctx.fillStyle = "#64748b";
      ctx.font = "16px system-ui";
      ctx.textAlign = "center";
      ctx.fillText("Waiting for video...", w / 2, h / 2);
    }
    
    // Draw frame counter (trimmed)
    ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
    ctx.fillRect(10, h - 40, 180, 30);
    ctx.fillStyle = "#e2e8f0";
    ctx.font = "bold 14px monospace";
    ctx.textAlign = "left";
    ctx.fillText(`Frame ${relativeFrame} / ${trimmedTotalFrames}`, 18, h - 20);
    
  }, [videoRef, keypoints, relativeFrame, trimmedTotalFrames]);

  // Animation loop for real-time sync
  useEffect(() => {
    const animate = () => {
      drawFrame();
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [drawFrame]);

  // Resize canvas to match container
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        canvas.width = width * window.devicePixelRatio;
        canvas.height = height * window.devicePixelRatio;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        
        const ctx = canvas.getContext("2d");
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
    });
    
    resizeObserver.observe(canvas.parentElement);
    
    return () => resizeObserver.disconnect();
  }, []);

  return (
    <div className="skeleton-overlay">
      <div className="skeleton-overlay__header">
        <span>🦴 Skeleton Overlay</span>
        <div className="skeleton-overlay__legend">
          <span className="legend-item"><span className="dot face"></span>Face</span>
          <span className="legend-item"><span className="dot arms"></span>Arms</span>
          <span className="legend-item"><span className="dot legs"></span>Legs</span>
        </div>
      </div>
      <div className="skeleton-overlay__canvas-container">
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
}

SkeletonOverlay.propTypes = {
  videoRef: PropTypes.object,
  keypoints: PropTypes.array,
  currentFrame: PropTypes.number,
  totalFrames: PropTypes.number,
  trimStart: PropTypes.number,
  trimEnd: PropTypes.number,
  fps: PropTypes.number,
};

export default SkeletonOverlay;

