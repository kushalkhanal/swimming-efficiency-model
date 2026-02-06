import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ComparisonView from '../components/ComparisonView';
import ComparisonMetrics from '../components/ComparisonMetrics';
import { useFormattedKeypoints } from '../hooks/useFormattedKeypoints';
import { useVideoMetrics } from '../hooks/useVideoMetrics';
import './ComparisonPage.css';

/**
 * Dedicated page for side-by-side video comparison
 */
function ComparisonPage() {
    const navigate = useNavigate();
    const [userVideos, setUserVideos] = useState([]);
    const [professionalVideos, setProfessionalVideos] = useState({
        freestyle: [],
        backstroke: [],
        breaststroke: [],
        butterfly: []
    });
    const [selectedUserVideo, setSelectedUserVideo] = useState(null);
    const [selectedReference, setSelectedReference] = useState(null);
    const [referenceType, setReferenceType] = useState('user'); // 'user' or 'professional'
    const fileInputRef = useRef(null);

    // Fetch keypoints for both videos
    const { keypointsData: userKeypoints } = useFormattedKeypoints(selectedUserVideo?.id);
    const { keypointsData: refKeypoints } = useFormattedKeypoints(selectedReference?.id);

    // Fetch metrics for comparison
    const { metrics: userMetrics } = useVideoMetrics(selectedUserVideo?.id);
    const { metrics: refMetrics } = useVideoMetrics(selectedReference?.id);

    // Fetch user uploaded videos with deduplication
    useEffect(() => {
        const fetchVideos = async () => {
            try {
                // Get videos from localStorage
                const storedVideos = JSON.parse(localStorage.getItem('uploadedVideos') || '[]');

                // Deduplicate by video NAME to remove visual duplicates
                // This handles cases where the same file was uploaded multiple times with different IDs
                const videoMap = new Map();
                storedVideos.forEach(video => {
                    if (video && video.name) {
                        // Using name as key means we only keep the LAST (latest) uploaded version of videos with the same name
                        videoMap.set(video.name, video);
                    }
                });
                const uniqueVideos = Array.from(videoMap.values());

                // Save cleaned list back to localStorage if duplicates were found
                if (uniqueVideos.length !== storedVideos.length) {
                    localStorage.setItem('uploadedVideos', JSON.stringify(uniqueVideos));
                }

                if (uniqueVideos.length > 0) {
                    setUserVideos(uniqueVideos);

                    // If we have 2+ videos, use first as reference and last as user video
                    if (uniqueVideos.length >= 2) {
                        setSelectedReference(uniqueVideos[0]);
                        setSelectedUserVideo(uniqueVideos[uniqueVideos.length - 1]);
                        setReferenceType('user');
                    } else if (uniqueVideos.length === 1) {
                        // Only one video - select it but no reference yet
                        setSelectedUserVideo(uniqueVideos[0]);
                        setSelectedReference(null);
                    }
                }
            } catch (error) {
                // Silently handle errors
            }
        };

        fetchVideos();
    }, []);

    // Fetch professional reference videos
    useEffect(() => {
        const fetchProfessionalVideos = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/v1/reference-videos');
                setProfessionalVideos(response.data);
            } catch (error) {
                // Silently fail if no professional videos available
            }
        };

        fetchProfessionalVideos();
    }, []);

    const handleVideoSelect = (video) => {
        setSelectedUserVideo(video);
    };

    const handleReferenceSelect = (video, type) => {
        setSelectedReference(video);
        setReferenceType(type);
    };

    const handleBackToDashboard = () => {
        navigate('/');
    };

    const handleLocalFileUpload = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('video/')) {
            const blobUrl = URL.createObjectURL(file);
            const localVideo = {
                id: `local_${Date.now()}`,
                name: file.name,
                src: blobUrl,
                isLocal: true
            };
            setSelectedUserVideo(localVideo);
        }
    };

    // Count total professional videos
    const totalProfessionalVideos = Object.values(professionalVideos).reduce(
        (sum, videos) => sum + videos.length,
        0
    );

    return (
        <div className="comparison-page">
            {/* Header */}
            <div className="comparison-header">
                <button className="back-button" onClick={handleBackToDashboard}>
                    ← Back to Dashboard
                </button>
                <h1>Side-by-Side Comparison</h1>
            </div>

            {/* Video Selectors */}
            <div className="comparison-selectors">
                {/* User Video Selector */}
                <div className="selector-group">
                    <label>YOUR VIDEO:</label>
                    <div className="video-input-group">
                        <select
                            value={selectedUserVideo?.isLocal ? '' : selectedUserVideo?.id || ''}
                            onChange={(e) => {
                                const video = userVideos.find(v => v.id === e.target.value);
                                handleVideoSelect(video);
                            }}
                            disabled={userVideos.length === 0}
                        >
                            {userVideos.length === 0 ? (
                                <option>No videos uploaded</option>
                            ) : (
                                <>
                                    <option value="">Select a video...</option>
                                    {userVideos.map((video) => (
                                        <option key={video.id} value={video.id}>
                                            📹 {video.name}
                                        </option>
                                    ))}
                                </>
                            )}
                        </select>
                        <div className="or-divider">OR</div>
                        <button
                            className="upload-local-btn"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            📁 Choose from Computer
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/*"
                            onChange={handleLocalFileUpload}
                            style={{ display: 'none' }}
                        />
                    </div>
                    {selectedUserVideo?.isLocal && (
                        <div className="selected-local-video">
                            ✓ Selected: {selectedUserVideo.name}
                        </div>
                    )}
                </div>

                <div className="vs-divider">VS</div>

                {/* Reference Video Selector */}
                <div className="selector-group">
                    <label>REFERENCE VIDEO:</label>

                    {/* Professional References Section */}
                    {totalProfessionalVideos > 0 && (
                        <div className="professional-references">
                            <div className="reference-section-header">
                                🏊 Professional References:
                            </div>

                            {Object.entries(professionalVideos).map(([stroke, videos]) => (
                                videos.length > 0 && (
                                    <div key={stroke} className="stroke-category">
                                        <div className="stroke-label">
                                            {stroke === 'freestyle' && '🏊‍♂️'}
                                            {stroke === 'backstroke' && '🏊‍♀️'}
                                            {stroke === 'breaststroke' && '🏊'}
                                            {stroke === 'butterfly' && '🦋'}
                                            {' ' + stroke.charAt(0).toUpperCase() + stroke.slice(1)}
                                        </div>
                                        {videos.map((video) => (
                                            <button
                                                key={video.id}
                                                className={`reference-btn ${selectedReference?.id === video.id ? 'selected' : ''
                                                    }`}
                                                onClick={() => handleReferenceSelect(video, 'professional')}
                                            >
                                                {video.swimmer}
                                            </button>
                                        ))}
                                    </div>
                                )
                            ))}
                        </div>
                    )}

                    {/* User Videos as Reference */}
                    {userVideos.length > 1 && (
                        <div className="user-references">
                            <div className="reference-section-header">
                                📹 Your Other Videos:
                            </div>
                            <select
                                value={referenceType === 'user' ? selectedReference?.id || '' : ''}
                                onChange={(e) => {
                                    const video = userVideos.find(v => v.id === e.target.value);
                                    if (video) {
                                        handleReferenceSelect(video, 'user');
                                    }
                                }}
                            >
                                <option value="">Select a video...</option>
                                {userVideos
                                    .filter(v => v.id !== selectedUserVideo?.id)
                                    .map((video) => (
                                        <option key={video.id} value={video.id}>
                                            {video.name}
                                        </option>
                                    ))}
                            </select>
                        </div>
                    )}

                    {/* No references available */}
                    {userVideos.length <= 1 && totalProfessionalVideos === 0 && (
                        <div className="no-references">
                            No reference videos available. Upload more videos or add professional references.
                        </div>
                    )}
                </div>
            </div>

            {/* Main Comparison View */}
            {selectedUserVideo && selectedReference ? (
                <>
                    <ComparisonView
                        leftVideo={selectedUserVideo.src}
                        rightVideo={
                            referenceType === 'professional'
                                ? `http://localhost:8000${selectedReference.videoUrl}`
                                : selectedReference.src
                        }
                        leftLabel={selectedUserVideo.name}
                        rightLabel={selectedReference.name || selectedReference.swimmer}
                        leftKeypoints={userKeypoints}
                        rightKeypoints={refKeypoints}
                    />

                    {/* Performance Comparison Metrics */}
                    <ComparisonMetrics
                        userMetrics={userMetrics}
                        referenceMetrics={refMetrics}
                        userVideoName={selectedUserVideo.name}
                        referenceVideoName={selectedReference.name || selectedReference.swimmer}
                    />
                </>
            ) : (
                <div className="no-selection">
                    <div className="no-selection-content">
                        <h2>👆 Select Videos to Compare</h2>
                        {userVideos.length === 0 ? (
                            <>
                                <p>You haven't uploaded any videos yet.</p>
                                <button
                                    className="upload-prompt-btn"
                                    onClick={() => navigate('/')}
                                >
                                    Go to Dashboard to Upload
                                </button>
                            </>
                        ) : userVideos.length === 1 ? (
                            <>
                                <p>Upload at least one more video or select a professional reference.</p>
                                {totalProfessionalVideos === 0 && (
                                    <p className="hint">
                                        💡 Add professional reference videos to compare your technique with Olympic swimmers!
                                    </p>
                                )}
                            </>
                        ) : (
                            <p>Select your video and a reference video to see the comparison.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ComparisonPage;
