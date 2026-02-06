/**
 * 2D skeleton drawing utilities for canvas rendering.
 */

import { SKELETON, COLORS, getJointColor, getBoneColor } from './skeletonStructure';

/**
 * Draw 2D skeleton overlay on canvas
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {HTMLVideoElement} videoElement - Video element to draw frame from
 * @param {Object} keypoints - Keypoints data for current frame
 * @param {number} canvasWidth - Canvas width
 * @param {number} canvasHeight - Canvas height
 * @param {Object} ratings - Biomechanical quality ratings for joints (optional)
 */
export function draw2DOverlay(ctx, videoElement, keypoints, canvasWidth, canvasHeight, ratings = {}) {
  // Clear canvas
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);

  // Step 1: ALWAYS draw current video frame if video element exists
  let videoDrawn = false;
  if (videoElement && videoElement.readyState >= 2) {
    try {
      ctx.drawImage(videoElement, 0, 0, canvasWidth, canvasHeight);
      videoDrawn = true;
    } catch (error) {
      console.warn('Failed to draw video frame:', error);
      // Video not ready, draw dark background
      ctx.fillStyle = '#0F172A';
      ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    }
  } else {
    // No video or not ready, draw dark background
    ctx.fillStyle = '#0F172A';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    if (videoElement) {
      console.debug('Video not ready yet, readyState:', videoElement.readyState);
    }
  }

  // Step 2: Draw skeleton on top of video if keypoints exist
  if (!keypoints) {
    // Only show message if video was also not drawn
    if (!videoDrawn) {
      ctx.fillStyle = '#94A3B8';
      ctx.font = '16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(
        'No skeleton data for this frame',
        canvasWidth / 2,
        canvasHeight / 2
      );
    }
    return;
  }

  // Draw bones first (below joints)
  drawBones(ctx, keypoints, canvasWidth, canvasHeight, ratings);

  // Draw joints on top
  drawJoints(ctx, keypoints, canvasWidth, canvasHeight);
}

/**
 * Draw skeleton bones (lines connecting joints)
 */
function drawBones(ctx, keypoints, canvasWidth, canvasHeight, ratings = {}) {
  Object.entries(SKELETON).forEach(([bodyPart, connections]) => {
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    connections.forEach(([joint1, joint2]) => {
      const p1 = keypoints[joint1];
      const p2 = keypoints[joint2];

      // Only draw if both joints exist and have good confidence
      if (p1 && p2 && p1.confidence > 0.5 && p2.confidence > 0.5) {
        // Get dynamic color based on biomechanical rating
        ctx.strokeStyle = getBoneColor(joint1, joint2, ratings);

        // Convert normalized coordinates to pixel coordinates if needed
        const x1 = p1.x <= 1 ? p1.x * canvasWidth : p1.x;
        const y1 = p1.y <= 1 ? p1.y * canvasHeight : p1.y;
        const x2 = p2.x <= 1 ? p2.x * canvasWidth : p2.x;
        const y2 = p2.y <= 1 ? p2.y * canvasHeight : p2.y;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    });
  });
}

/**
 * Draw skeleton joints (circles)
 */
function drawJoints(ctx, keypoints, canvasWidth, canvasHeight) {
  Object.entries(keypoints).forEach(([jointName, joint]) => {
    if (!joint || joint.confidence < 0.5) return; // Skip low confidence

    // Determine color based on body part
    const color = getJointColor(jointName);

    // Convert normalized coordinates to pixel coordinates if needed
    const x = joint.x <= 1 ? joint.x * canvasWidth : joint.x;
    const y = joint.y <= 1 ? joint.y * canvasHeight : joint.y;

    // Draw joint circle with shadow for visibility
    const radius = 6;

    // Shadow
    ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
    ctx.shadowBlur = 4;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;

    // Fill circle
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fill();

    // Stroke circle (white border)
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Reset shadow
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
  });
}

