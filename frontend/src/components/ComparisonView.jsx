import { useState, useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { draw2DOverlay } from '../utils/draw2D';
import BiomechLegend from './BiomechLegend';
import './ComparisonView.css';

/**
 * Side-by-side video comparison with synchronized playback
 */
function ComparisonView({
    leftVideo,
    rightVideo,
    leftKeypoints,
    rightKeypoints,
    leftLabel = "Your Session",
    rightLabel = "Gold Standard"
}) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentFrame, setCurrentFrame] = useState(0);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [showSkeletons, setShowSkeletons] = useState(true);
    const [videoError, setVideoError] = useState({ left: false, right: false });

    const leftVideoRef = useRef(null);
    const rightVideoRef = useRef(null);
    const leftCanvasRef = useRef(null);
    const rightCanvasRef = useRef(null);
    const animationFrameRef = useRef(null);

    // Handle video errors
    const handleVideoError = useCallback((side, error) => {
        console.error(`Video error (${side}):`, error);
        setVideoError(prev => ({ ...prev, [side]: true }));
    }, []);

    // Synchronized play/pause
    const handlePlayPause = useCallback(() => {
        const leftVid = leftVideoRef.current;
        const rightVid = rightVideoRef.current;

        if (!leftVid || !rightVid) return;

        if (isPlaying) {
            leftVid.pause();
            rightVid.pause();
            setIsPlaying(false);
        } else {
            leftVid.play();
            rightVid.play();
            setIsPlaying(true);
        }
    }, [isPlaying]);

    // Synchronized frame update
    const updateFrame = useCallback(() => {
        const leftVid = leftVideoRef.current;
        const rightVid = rightVideoRef.current;

        if (!leftVid || !rightVid) return;

        // Calculate frame based on left video
        const fps = 30; // Default FPS
        const frame = Math.floor(leftVid.currentTime * fps);
        setCurrentFrame(frame);

        // Sync right video to same time
        if (Math.abs(rightVid.currentTime - leftVid.currentTime) > 0.1) {
            rightVid.currentTime = leftVid.currentTime;
        }

        // Draw skeletons
        drawSkeletons();

        if (isPlaying) {
            animationFrameRef.current = requestAnimationFrame(updateFrame);
        }
    }, [isPlaying]);

    // Draw skeleton overlays
    const drawSkeletons = useCallback(() => {
        const leftCanvas = leftCanvasRef.current;
        const rightCanvas = rightCanvasRef.current;
        const leftVid = leftVideoRef.current;
        const rightVid = rightVideoRef.current;

        if (!leftCanvas || !rightCanvas || !leftVid || !rightVid) return;
        if (!showSkeletons) return;

        const leftCtx = leftCanvas.getContext('2d');
        const rightCtx = rightCanvas.getContext('2d');

        const leftKp = leftKeypoints?.[currentFrame];
        const rightKp = rightKeypoints?.[currentFrame];

        // Draw left skeleton
        draw2DOverlay(leftCtx, leftVid, leftKp, leftCanvas.width, leftCanvas.height);

        // Draw right skeleton
        draw2DOverlay(rightCtx, rightVid, rightKp, rightCanvas.width, rightCanvas.height);
    }, [currentFrame, leftKeypoints, rightKeypoints, showSkeletons]);

    // Speed control
    const handleSpeedChange = useCallback((speed) => {
        setPlaybackSpeed(speed);
        if (leftVideoRef.current) leftVideoRef.current.playbackRate = speed;
        if (rightVideoRef.current) rightVideoRef.current.playbackRate = speed;
    }, []);

    // Update loop
    useEffect(() => {
        if (isPlaying) {
            animationFrameRef.current = requestAnimationFrame(updateFrame);
        }
        return () => {
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, [isPlaying, updateFrame]);

    // Resize canvases to match video intrinsic dimensions
    // CSS object-fit:contain will letterbox them identically to videos
    useEffect(() => {
        const leftVid = leftVideoRef.current;
        const rightVid = rightVideoRef.current;

        const resizeCanvas = (video, canvas) => {
            if (!video || !canvas || video.videoWidth === 0) return;

            // Set canvas to video's intrinsic dimensions
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };

        const setupResize = (video, canvas) => {
            if (!video || !canvas) return;

            const handleResize = () => resizeCanvas(video, canvas);

            // Resize when metadata loads
            if (video.readyState >= 2) {
                handleResize();
            } else {
                video.addEventListener('loadedmetadata', handleResize, { once: true });
            }

            return () => {
                video.removeEventListener('loadedmetadata', handleResize);
            };
        };

        const leftCleanup = setupResize(leftVid, leftCanvasRef.current);
        const rightCleanup = setupResize(rightVid, rightCanvasRef.current);

        return () => {
            if (leftCleanup) leftCleanup();
            if (rightCleanup) rightCleanup();
        };
    }, [leftVideo, rightVideo]);

    return (
        <div className="comparison-view">
            {/* Header */}
            <div className="comparison-header">
                <h2>Side-by-Side Comparison</h2>
                <div className="comparison-controls">
                    <label>
                        <input
                            type="checkbox"
                            checked={showSkeletons}
                            onChange={(e) => setShowSkeletons(e.target.checked)}
                        />
                        Show Skeletons
                    </label>
                </div>
            </div>

            {/* Split video panels */}
            <div className="comparison-panels">
                {/* Left panel */}
                <div className="comparison-panel">
                    <div className="panel-label">{leftLabel}</div>
                    <div className="video-container">
                        <video
                            ref={leftVideoRef}
                            src={leftVideo}
                            className="comparison-video"
                            onError={(e) => handleVideoError('left', e)}
                        />
                        {videoError.left && (
                            <div style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                transform: 'translate(-50%, -50%)',
                                color: '#ef4444',
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                padding: '16px',
                                borderRadius: '8px',
                                textAlign: 'center'
                            }}>
                                ⚠️ Failed to load video
                            </div>
                        )}
                        <canvas
                            ref={leftCanvasRef}
                            className="comparison-canvas"
                        />
                    </div>
                </div>

                {/* Divider */}
                <div className="comparison-divider" />

                {/* Right panel */}
                <div className="comparison-panel">
                    <div className="panel-label">{rightLabel}</div>
                    <div className="video-container">
                        <video
                            ref={rightVideoRef}
                            src={rightVideo}
                            className="comparison-video"
                            onError={(e) => handleVideoError('right', e)}
                        />
                        {videoError.right && (
                            <div style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                transform: 'translate(-50%, -50%)',
                                color: '#ef4444',
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                padding: '16px',
                                borderRadius: '8px',
                                textAlign: 'center'
                            }}>
                                ⚠️ Failed to load video
                            </div>
                        )}
                        <canvas
                            ref={rightCanvasRef}
                            className="comparison-canvas"
                        />
                    </div>
                </div>
            </div>

            {/* Legend */}
            {showSkeletons && <BiomechLegend show={showSkeletons} />}

            {/* Unified controls */}
            <div className="comparison-playback-controls">
                <button onClick={handlePlayPause} className="control-btn play-btn">
                    {isPlaying ? '⏸ Pause' : '▶ Play'}
                </button>

                <span className="frame-display">Frame: {currentFrame}</span>

                <div className="speed-controls">
                    <label>Speed:</label>
                    {[0.25, 0.5, 1, 1.5, 2].map(speed => (
                        <button
                            key={speed}
                            onClick={() => handleSpeedChange(speed)}
                            className={`speed-btn ${playbackSpeed === speed ? 'active' : ''}`}
                        >
                            {speed}x
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

ComparisonView.propTypes = {
    leftVideo: PropTypes.string.isRequired,
    rightVideo: PropTypes.string.isRequired,
    leftKeypoints: PropTypes.object,
    rightKeypoints: PropTypes.object,
    leftLabel: PropTypes.string,
    rightLabel: PropTypes.string,
};

export default ComparisonView;
