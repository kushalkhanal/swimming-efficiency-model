/**
 * Skeleton structure definitions for 2D and 3D pose visualization.
 * Defines bone connections and color coding.
 */

export const SKELETON = {
  face: [
    ['nose', 'left_eye_inner'],
    ['nose', 'right_eye_inner'],
    ['left_eye_inner', 'left_eye'],
    ['right_eye_inner', 'right_eye'],
    ['left_eye', 'left_eye_outer'],
    ['right_eye', 'right_eye_outer'],
    ['left_eye_outer', 'left_ear'],
    ['right_eye_outer', 'right_ear'],
  ],
  arms: [
    ['left_shoulder', 'left_elbow'],
    ['left_elbow', 'left_wrist'],
    ['left_wrist', 'left_index'],
    ['left_wrist', 'left_pinky'],
    ['left_index', 'left_thumb'],
    ['right_shoulder', 'right_elbow'],
    ['right_elbow', 'right_wrist'],
    ['right_wrist', 'right_index'],
    ['right_wrist', 'right_pinky'],
    ['right_index', 'right_thumb'],
  ],
  legs: [
    ['left_hip', 'left_knee'],
    ['left_knee', 'left_ankle'],
    ['left_ankle', 'left_heel'],
    ['left_ankle', 'left_foot_index'],
    ['right_hip', 'right_knee'],
    ['right_knee', 'right_ankle'],
    ['right_ankle', 'right_heel'],
    ['right_ankle', 'right_foot_index'],
  ],
  torso: [
    ['left_shoulder', 'right_shoulder'],
    ['left_shoulder', 'left_hip'],
    ['right_shoulder', 'right_hip'],
    ['left_hip', 'right_hip'],
  ],
};

export const COLORS = {
  face: '#F59E0B',    // Amber 🟠
  arms: '#3B82F6',    // Blue 🔵
  legs: '#10B981',    // Green 🟢
  torso: '#FFFFFF',   // White ⚪
};

/**
 * Biomechanical quality rating colors
 */
export const BIOMECH_COLORS = {
  excellent: '#10B981',  // Green - Optimal biomechanics
  good: '#3B82F6',       // Blue - Minor improvements possible
  needs_work: '#F59E0B', // Amber/Orange - Form issues detected
  poor: '#EF4444',       // Red - Significant correction needed
  default: '#FFFFFF'     // White - No rating data available
};

/**
 * Get color for a bone based on biomechanical rating
 */
export function getBoneColor(joint1, joint2, ratings = {}) {
  // Determine which joint's rating to use (the distal joint)
  // For example, for shoulder-elbow bone, use elbow rating
  let ratingKey = null;

  // Map bones to their relevant joint ratings
  if (joint2.includes('elbow')) {
    ratingKey = joint2; // e.g., 'left_elbow', 'right_elbow'
  } else if (joint2.includes('wrist') && joint1.includes('elbow')) {
    ratingKey = joint1; // For elbow-wrist, use elbow rating
  } else if (joint2.includes('shoulder')) {
    ratingKey = joint2;
  } else if (joint2.includes('knee')) {
    ratingKey = joint2;
  } else if (joint2.includes('ankle') && joint1.includes('knee')) {
    ratingKey = joint1;
  }

  // Get rating and return corresponding color
  if (ratingKey && ratings[ratingKey]) {
    return BIOMECH_COLORS[ratings[ratingKey]] || BIOMECH_COLORS.default;
  }

  // Fallback to default body part colors
  return BIOMECH_COLORS.default;
}

/**
 * Get color for a joint based on its name
 */
export function getJointColor(jointName) {
  const name = jointName.toLowerCase();

  if (name.includes('eye') || name.includes('ear') || name === 'nose' || name.includes('mouth')) {
    return COLORS.face;
  } else if (name.includes('shoulder') || name.includes('elbow') || name.includes('wrist') ||
    name.includes('pinky') || name.includes('index') || name.includes('thumb')) {
    return COLORS.arms;
  } else if (name.includes('hip') || name.includes('knee') || name.includes('ankle') ||
    name.includes('heel') || name.includes('foot')) {
    return COLORS.legs;
  } else {
    return COLORS.torso;
  }
}

/**
 * Check if a joint is part of a specific body part
 */
export function getBodyPart(jointName) {
  const name = jointName.toLowerCase();

  if (name.includes('eye') || name.includes('ear') || name === 'nose' || name.includes('mouth')) {
    return 'face';
  } else if (name.includes('shoulder') || name.includes('elbow') || name.includes('wrist') ||
    name.includes('pinky') || name.includes('index') || name.includes('thumb')) {
    return 'arms';
  } else if (name.includes('hip') || name.includes('knee') || name.includes('ankle') ||
    name.includes('heel') || name.includes('foot')) {
    return 'legs';
  } else {
    return 'torso';
  }
}

