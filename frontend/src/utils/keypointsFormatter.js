/**
 * Utility functions to format keypoints data for the swim analysis components
 */

/**
 * Convert backend keypoints format to frame-indexed format
 * Backend format: Array of frames with keypoints arrays
 * Target format: { frameNumber: { keypointName: { x, y, z, confidence } } }
 */
export function formatKeypointsForFrames(keypointsArray, frameIndices = []) {
  if (!keypointsArray || keypointsArray.length === 0) {
    return {};
  }

  // MediaPipe Pose landmark names (33 keypoints)
  const landmarkNames = [
    'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 'right_eye_inner',
    'right_eye', 'right_eye_outer', 'left_ear', 'right_ear', 'mouth_left',
    'mouth_right', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
    'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky', 'left_index',
    'right_index', 'left_thumb', 'right_thumb', 'left_hip', 'right_hip',
    'left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'left_heel',
    'right_heel', 'left_foot_index', 'right_foot_index'
  ];

  const formatted = {};

  keypointsArray.forEach((keypoints, index) => {
    const frameIndex = frameIndices[index] !== undefined ? frameIndices[index] : index;
    
    if (!keypoints || keypoints.length !== 33) {
      return; // Skip invalid keypoints
    }

    const frameKeypoints = {};
    
    keypoints.forEach((point, i) => {
      if (i < landmarkNames.length) {
        const name = landmarkNames[i];
        // Keypoints format: [x, y, z, visibility]
        // x, y are normalized (0-1), z is relative depth, visibility is confidence
        frameKeypoints[name] = {
          x: point[0] || 0,
          y: point[1] || 0,
          z: point[2] || 0,
          confidence: point[3] || 0
        };
      }
    });

    formatted[frameIndex] = frameKeypoints;
  });

  return formatted;
}

/**
 * Convert keypoints from API response format
 * API format: { frames: [{ frame_index, keypoints }] }
 */
export function formatKeypointsFromAPI(apiResponse) {
  if (!apiResponse || !apiResponse.frames || !Array.isArray(apiResponse.frames)) {
    return {};
  }

  const landmarkNames = [
    'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 'right_eye_inner',
    'right_eye', 'right_eye_outer', 'left_ear', 'right_ear', 'mouth_left',
    'mouth_right', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
    'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky', 'left_index',
    'right_index', 'left_thumb', 'right_thumb', 'left_hip', 'right_hip',
    'left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'left_heel',
    'right_heel', 'left_foot_index', 'right_foot_index'
  ];

  const formatted = {};

  apiResponse.frames.forEach((frame) => {
    const frameIndex = frame.frame_index;
    const keypoints = frame.keypoints || [];

    if (!Array.isArray(keypoints) || keypoints.length !== 33) {
      return;
    }

    const frameKeypoints = {};
    
    keypoints.forEach((point, i) => {
      if (i < landmarkNames.length && Array.isArray(point) && point.length >= 4) {
        const name = landmarkNames[i];
        frameKeypoints[name] = {
          x: point[0] || 0,
          y: point[1] || 0,
          z: point[2] || 0,
          confidence: point[3] || 0
        };
      }
    });

    formatted[frameIndex] = frameKeypoints;
  });

  return formatted;
}

/**
 * Convert single frame keypoints (from useKeypoints hook)
 */
export function formatSingleFrameKeypoints(keypoints, frameIndex) {
  if (!keypoints || !Array.isArray(keypoints) || keypoints.length !== 33) {
    return null;
  }

  const landmarkNames = [
    'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 'right_eye_inner',
    'right_eye', 'right_eye_outer', 'left_ear', 'right_ear', 'mouth_left',
    'mouth_right', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
    'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky', 'left_index',
    'right_index', 'left_thumb', 'right_thumb', 'left_hip', 'right_hip',
    'left_knee', 'right_knee', 'left_ankle', 'right_ankle', 'left_heel',
    'right_heel', 'left_foot_index', 'right_foot_index'
  ];

  const formatted = {};
  
  keypoints.forEach((point, i) => {
    if (i < landmarkNames.length && Array.isArray(point) && point.length >= 4) {
      const name = landmarkNames[i];
      formatted[name] = {
        x: point[0] || 0,
        y: point[1] || 0,
        z: point[2] || 0,
        confidence: point[3] || 0
      };
    }
  });

  return formatted;
}

