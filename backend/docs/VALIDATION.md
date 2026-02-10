# Validation & Performance Analysis

## 1. System Accuracy Metrics

### 1.1 Swimmer Detection (YOLOv8)
The system employs **YOLOv8** for initial swimmer localization. Performance varies by water turbulence and lighting conditions:

| Condition | Accuracy (mAP) | Notes |
|-----------|----------------|-------|
| **Clear Footage** | **85-90%** | Optimal lighting, minimal splash, clear lane separation |
| **Turbulent** | **60-70%** | High splash (starts/turns), bubbles, low contrast |
| **Underwater** | **75-80%** | Variable refraction, good visibility required |

### 1.2 Pose Estimation (MediaPipe BlazePose)
Skeletal tracking accuracy determines the validity of biomechanical metrics:

- **General Accuracy**: **96.4% PCK@0.2** (Percentage of Correct Keypoints within 20% of torso diameter)
- **Underwater degradation**: Slight reduction in accuracy due to light refraction and bubble occlusion.
- **Occlusion Handling**: Robust prediction of occluded limbs during crossover phases.

### 1.3 Processing Performance
| Metric | Value | Hardware |
|--------|-------|----------|
| **Latency** | **30-45ms/frame** | Standard CPU (No GPU required) |
| **Throughput** | **20-30 FPS** | Real-time analysis capability |

---

## 2. Stroke-Specific Findings

The biomechanical model was evaluated across all four competitive strokes, with optimizations prioritized for Freestyle.

### 2.1 Freestyle (Front Crawl)
- **Status**: **Fully Validated**
- **Phase Detection**: High accuracy (>92%) for Catch per Pull per Recovery segmentation.
- **Key Metrics**: Body roll and stroke rate are highly reliable.

### 2.2 Backstroke
- **Status**: **Validated**
- **Challenges**: Surface reflection can affect shoulder visibility during rotation.
- **Accuracy**: Comparable to freestyle for stroke rate; slightly lower for underwater arm traction.

### 2.3 Breaststroke & Butterfly
- **Status**: **Experimental / Generalized Support**
- **Phase Detection**: Uses generalized velocity thresholds. May require manual calibration for "Glide" phases in Breaststroke.
- **Symmetry**: Symmetry index is the primary reliable metric for these simultaneous-stroke styles.

---

## 3. Dataset & Methodology

### 3.1 Validation Dataset
The metrics above are derived from a diverse dataset designed to represent varying real-world conditions.

- **Total Videos Analyzed**: **~50 Clips**
- **Sources**: 
  - Standard Competition Footage (Olympics/World Championships broadcasts for "Ideal" technique)
  - Training Session Recordings (GoPro/Phone cameras for "Real-world" testing)
- **Swimmer Demographics**:
  - **Age Range**: 16-25 (Competitive/Collegiate level), 12-16 (Junior Competitive)
  - **Skill Levels**: Ranging from Club/Regional to Elite International.

### 3.2 Testing Protocol
1. **Ground Truth Comparison**: Automated keypoints compared against manual annotations for selected keyframes.
2. **Stroke Counting**: Automated stroke count compared against manual counting (Error rate < ±1 stroke per 100m).
3. **Temporal Consistency**: Smoothness of velocity curves analyzed to detect jitter/tracking loss.
