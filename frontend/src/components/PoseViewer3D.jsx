import { useRef, useMemo, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Grid, Html } from "@react-three/drei";
import PropTypes from "prop-types";
import "./PoseViewer3D.css";

// MediaPipe Pose connections (pairs of keypoint indices to connect)
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
  // Face (optional)
  [0, 11], // nose to left shoulder
  [0, 12], // nose to right shoulder
];

// Color scheme for body parts
const getJointColor = (index) => {
  if (index <= 10) return "#f59e0b"; // Face - amber
  if (index >= 11 && index <= 16) return "#3b82f6"; // Arms - blue
  if (index >= 17 && index <= 22) return "#8b5cf6"; // Hands - purple
  if (index >= 23 && index <= 28) return "#10b981"; // Legs - green
  return "#94a3b8"; // Default - gray
};

const getBoneColor = (startIdx, endIdx) => {
  // Arms
  if ([11, 13, 15].includes(startIdx) && [13, 15].includes(endIdx)) return "#3b82f6";
  if ([12, 14, 16].includes(startIdx) && [14, 16].includes(endIdx)) return "#3b82f6";
  // Legs
  if ([23, 25, 27].includes(startIdx) && [25, 27].includes(endIdx)) return "#10b981";
  if ([24, 26, 28].includes(startIdx) && [26, 28].includes(endIdx)) return "#10b981";
  // Torso
  return "#e2e8f0";
};

/**
 * Single joint sphere
 */
function Joint({ position, index }) {
  const color = getJointColor(index);
  const size = index === 0 ? 0.08 : 0.05; // Larger for head
  
  return (
    <mesh position={position}>
      <sphereGeometry args={[size, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
    </mesh>
  );
}

Joint.propTypes = {
  position: PropTypes.array.isRequired,
  index: PropTypes.number.isRequired,
};

/**
 * Bone connecting two joints
 */
function Bone({ start, end, startIdx, endIdx }) {
  const ref = useRef();
  
  const { position, rotation, length } = useMemo(() => {
    const midX = (start[0] + end[0]) / 2;
    const midY = (start[1] + end[1]) / 2;
    const midZ = (start[2] + end[2]) / 2;
    
    const dx = end[0] - start[0];
    const dy = end[1] - start[1];
    const dz = end[2] - start[2];
    const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
    
    // Calculate rotation to align cylinder with bone direction
    const rotX = Math.atan2(Math.sqrt(dx * dx + dz * dz), dy);
    const rotZ = Math.atan2(dx, dz);
    
    return {
      position: [midX, midY, midZ],
      rotation: [rotX, 0, -rotZ],
      length: len,
    };
  }, [start, end]);
  
  const color = getBoneColor(startIdx, endIdx);
  
  return (
    <mesh ref={ref} position={position} rotation={rotation}>
      <cylinderGeometry args={[0.02, 0.02, length, 8]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
}

Bone.propTypes = {
  start: PropTypes.array.isRequired,
  end: PropTypes.array.isRequired,
  startIdx: PropTypes.number.isRequired,
  endIdx: PropTypes.number.isRequired,
};

/**
 * Complete skeleton from keypoints
 */
function Skeleton({ keypoints3d }) {
  if (!keypoints3d || keypoints3d.length < 29) {
    return null;
  }
  
  // Convert keypoints to 3D positions (normalize and center)
  const positions = useMemo(() => {
    // Find center of mass (average of hip positions)
    const leftHip = keypoints3d[23] || [0, 0, 0];
    const rightHip = keypoints3d[24] || [0, 0, 0];
    const centerX = (leftHip[0] + rightHip[0]) / 2;
    const centerY = (leftHip[1] + rightHip[1]) / 2;
    const centerZ = (leftHip[2] + rightHip[2]) / 2;
    
    // Scale factor (adjust based on your data)
    const scale = 2.0;
    
    return keypoints3d.map((kp) => {
      if (!kp || kp.length < 3) return [0, 0, 0];
      return [
        (kp[0] - centerX) * scale,
        -(kp[1] - centerY) * scale, // Flip Y for proper orientation
        (kp[2] - centerZ) * scale,
      ];
    });
  }, [keypoints3d]);
  
  return (
    <group>
      {/* Render joints */}
      {positions.slice(0, 29).map((pos, idx) => (
        <Joint key={`joint-${idx}`} position={pos} index={idx} />
      ))}
      
      {/* Render bones */}
      {POSE_CONNECTIONS.map(([startIdx, endIdx], idx) => {
        const start = positions[startIdx];
        const end = positions[endIdx];
        if (!start || !end) return null;
        
        return (
          <Bone
            key={`bone-${idx}`}
            start={start}
            end={end}
            startIdx={startIdx}
            endIdx={endIdx}
          />
        );
      })}
    </group>
  );
}

Skeleton.propTypes = {
  keypoints3d: PropTypes.array,
};

/**
 * Animated skeleton that updates with frame changes
 */
function AnimatedSkeleton({ keypoints3d, isPlaying }) {
  const groupRef = useRef();
  
  // Gentle rotation when playing
  useFrame((state, delta) => {
    if (groupRef.current && isPlaying) {
      groupRef.current.rotation.y += delta * 0.1;
    }
  });
  
  return (
    <group ref={groupRef}>
      <Skeleton keypoints3d={keypoints3d} />
    </group>
  );
}

AnimatedSkeleton.propTypes = {
  keypoints3d: PropTypes.array,
  isPlaying: PropTypes.bool,
};

/**
 * Main 3D Pose Viewer component
 */
function PoseViewer3D({ 
  keypoints3d = null, 
  isPlaying = false,
  onClose = null,
  isFullscreen = false,
}) {
  const [viewPreset, setViewPreset] = useState("front");
  
  const cameraPositions = {
    front: [0, 0, 4],
    side: [4, 0, 0],
    top: [0, 4, 0],
    angle: [3, 2, 3],
  };
  
  // Generate sample keypoints if none provided
  const displayKeypoints = useMemo(() => {
    if (keypoints3d && keypoints3d.length >= 29) {
      return keypoints3d;
    }
    
    // Generate a sample T-pose skeleton for demo
    return [
      [0, 0.9, 0],      // 0: nose
      [0.03, 0.85, 0],  // 1: left eye inner
      [0.05, 0.85, 0],  // 2: left eye
      [0.07, 0.85, 0],  // 3: left eye outer
      [-0.03, 0.85, 0], // 4: right eye inner
      [-0.05, 0.85, 0], // 5: right eye
      [-0.07, 0.85, 0], // 6: right eye outer
      [0.08, 0.82, 0],  // 7: left ear
      [-0.08, 0.82, 0], // 8: right ear
      [0.03, 0.78, 0],  // 9: mouth left
      [-0.03, 0.78, 0], // 10: mouth right
      [0.2, 0.6, 0],    // 11: left shoulder
      [-0.2, 0.6, 0],   // 12: right shoulder
      [0.45, 0.6, 0],   // 13: left elbow
      [-0.45, 0.6, 0],  // 14: right elbow
      [0.7, 0.6, 0],    // 15: left wrist
      [-0.7, 0.6, 0],   // 16: right wrist
      [0.75, 0.6, 0],   // 17: left pinky
      [-0.75, 0.6, 0],  // 18: right pinky
      [0.78, 0.6, 0],   // 19: left index
      [-0.78, 0.6, 0],  // 20: right index
      [0.73, 0.6, 0],   // 21: left thumb
      [-0.73, 0.6, 0],  // 22: right thumb
      [0.12, 0.2, 0],   // 23: left hip
      [-0.12, 0.2, 0],  // 24: right hip
      [0.12, -0.2, 0],  // 25: left knee
      [-0.12, -0.2, 0], // 26: right knee
      [0.12, -0.6, 0],  // 27: left ankle
      [-0.12, -0.6, 0], // 28: right ankle
    ];
  }, [keypoints3d]);
  
  return (
    <div className={`pose-viewer-3d ${isFullscreen ? "fullscreen" : ""}`}>
      <div className="viewer-controls">
        <div className="view-presets">
          {Object.keys(cameraPositions).map((preset) => (
            <button
              key={preset}
              className={viewPreset === preset ? "active" : ""}
              onClick={() => setViewPreset(preset)}
            >
              {preset.charAt(0).toUpperCase() + preset.slice(1)}
            </button>
          ))}
        </div>
        {onClose && (
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        )}
      </div>
      
      <Canvas>
        <PerspectiveCamera
          makeDefault
          position={cameraPositions[viewPreset]}
          fov={50}
        />
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={2}
          maxDistance={10}
        />
        
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <directionalLight position={[-5, 5, -5]} intensity={0.5} />
        
        {/* Grid floor */}
        <Grid
          args={[10, 10]}
          position={[0, -1, 0]}
          cellSize={0.5}
          cellThickness={0.5}
          cellColor="#334155"
          sectionSize={2}
          sectionThickness={1}
          sectionColor="#475569"
          fadeDistance={10}
          fadeStrength={1}
          followCamera={false}
        />
        
        {/* Skeleton */}
        <AnimatedSkeleton keypoints3d={displayKeypoints} isPlaying={isPlaying} />
        
        {/* Info label */}
        {!keypoints3d && (
          <Html position={[0, 1.5, 0]} center>
            <div className="info-label">
              Sample pose - Upload video for real data
            </div>
          </Html>
        )}
      </Canvas>
      
      <div className="viewer-legend">
        <span><span className="dot face"></span> Face</span>
        <span><span className="dot arms"></span> Arms</span>
        <span><span className="dot legs"></span> Legs</span>
        <span><span className="dot torso"></span> Torso</span>
      </div>
    </div>
  );
}

PoseViewer3D.propTypes = {
  keypoints3d: PropTypes.array,
  isPlaying: PropTypes.bool,
  onClose: PropTypes.func,
  isFullscreen: PropTypes.bool,
};

export default PoseViewer3D;

