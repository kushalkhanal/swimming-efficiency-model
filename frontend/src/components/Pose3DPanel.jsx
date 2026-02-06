import { useEffect, useRef } from "react";
import PropTypes from "prop-types";

/**
 * Panel 3: 3D pose viewer with Three.js
 * Phase 1: Placeholder - will be implemented in Phase 4
 */
function Pose3DPanel({ keypoints, currentFrame }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // Phase 1: Just show placeholder
    // Phase 4: Will implement full 3D Three.js scene
    
    const container = containerRef.current;
    if (!container) return;

    // Clear container
    container.innerHTML = "";
    
    // Create placeholder div
    const placeholder = document.createElement("div");
    placeholder.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #94A3B8;
      font-family: sans-serif;
    `;
    
    const title = document.createElement("div");
    title.textContent = "3D Pose Viewer";
    title.style.cssText = "font-size: 18px; margin-bottom: 10px;";
    
    const frameInfo = document.createElement("div");
    frameInfo.textContent = `Frame: ${currentFrame}`;
    frameInfo.style.cssText = "font-size: 14px; margin-bottom: 10px;";
    
    const keypointInfo = document.createElement("div");
    keypointInfo.textContent = keypoints 
      ? "Keypoints available" 
      : "No keypoints for this frame";
    keypointInfo.style.cssText = "font-size: 12px;";
    
    placeholder.appendChild(title);
    placeholder.appendChild(frameInfo);
    placeholder.appendChild(keypointInfo);
    container.appendChild(placeholder);
    
    // Phase 4: Will initialize Three.js scene here
  }, [currentFrame, keypoints]);

  return (
    <div 
      ref={containerRef}
      className="pose-3d-container"
      style={{ width: "100%", height: "100%" }}
    />
  );
}

Pose3DPanel.propTypes = {
  keypoints: PropTypes.object,
  currentFrame: PropTypes.number.isRequired,
};

export default Pose3DPanel;

