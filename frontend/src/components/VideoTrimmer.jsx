import { useState, useRef, useEffect } from "react";
import "./VideoTrimmer.css";

/**
 * Video trimmer component that allows users to select a segment of the video to analyze.
 */
function VideoTrimmer({ videoFile, onConfirm, onCancel, maxDuration = 300 }) {
  const videoRef = useRef(null);
  const [duration, setDuration] = useState(0);
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);

  // Create object URL for video preview
  useEffect(() => {
    if (videoFile) {
      console.log("[VideoTrimmer] Received videoFile:");
      console.log("[VideoTrimmer]   name:", videoFile.name);
      console.log("[VideoTrimmer]   size:", videoFile.size, "bytes");
      console.log("[VideoTrimmer]   type:", videoFile.type);
      const url = URL.createObjectURL(videoFile);
      console.log("[VideoTrimmer]   objectURL:", url);
      setVideoUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [videoFile]);

  // Handle video metadata loaded
  const handleLoadedMetadata = () => {
    const video = videoRef.current;
    if (video) {
      const dur = video.duration;
      console.log("[VideoTrimmer] Video metadata loaded:");
      console.log("[VideoTrimmer]   duration:", dur);
      console.log("[VideoTrimmer]   duration (isFinite):", isFinite(dur));
      console.log("[VideoTrimmer]   duration (isNaN):", isNaN(dur));
      console.log("[VideoTrimmer]   maxDuration:", maxDuration);
      console.log("[VideoTrimmer]   videoWidth:", video.videoWidth);
      console.log("[VideoTrimmer]   videoHeight:", video.videoHeight);
      console.log("[VideoTrimmer]   readyState:", video.readyState);
      console.log("[VideoTrimmer]   networkState:", video.networkState);
      console.log("[VideoTrimmer]   src:", video.src);
      
      // If duration is invalid, try to get it differently
      if (!isFinite(dur) || dur <= 0) {
        console.log("[VideoTrimmer] Invalid duration, waiting for more data...");
        return;
      }
      
      setDuration(dur);
      setStartTime(0);
      // Default end time: min of video duration or maxDuration
      setEndTime(Math.min(dur, maxDuration));
    }
  };
  
  // Also listen for durationchange event
  const handleDurationChange = () => {
    const video = videoRef.current;
    if (video && isFinite(video.duration) && video.duration > 0) {
      console.log("[VideoTrimmer] Duration changed to:", video.duration);
      if (duration === 0 || duration !== video.duration) {
        setDuration(video.duration);
        setEndTime(Math.min(video.duration, maxDuration));
      }
    }
  };

  // Update current time during playback
  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (video) {
      setCurrentTime(video.currentTime);
      // Loop within selected range
      if (video.currentTime >= endTime) {
        video.currentTime = startTime;
      }
    }
  };

  // Handle start time change
  const handleStartChange = (e) => {
    const newStart = parseFloat(e.target.value);
    setStartTime(newStart);
    // Ensure end time maintains max duration constraint
    if (endTime - newStart > maxDuration) {
      setEndTime(newStart + maxDuration);
    }
    if (newStart >= endTime) {
      setEndTime(Math.min(newStart + 1, duration));
    }
    // Seek video to start position
    if (videoRef.current) {
      videoRef.current.currentTime = newStart;
    }
  };

  // Handle end time change
  const handleEndChange = (e) => {
    const newEnd = parseFloat(e.target.value);
    setEndTime(newEnd);
    // Ensure start time maintains max duration constraint
    if (newEnd - startTime > maxDuration) {
      setStartTime(newEnd - maxDuration);
    }
    if (newEnd <= startTime) {
      setStartTime(Math.max(newEnd - 1, 0));
    }
  };

  // Play/pause toggle
  const togglePlay = () => {
    const video = videoRef.current;
    if (video) {
      if (isPlaying) {
        video.pause();
      } else {
        video.currentTime = startTime;
        video.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // Format time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Calculate selected duration
  const selectedDuration = endTime - startTime;
  const isValidSelection = selectedDuration > 0 && selectedDuration <= maxDuration;

  // Handle confirm
  const handleConfirm = () => {
    if (isValidSelection) {
      const trimData = {
        startTime: Math.round(startTime * 1000) / 1000, // Round to 3 decimal places
        endTime: Math.round(endTime * 1000) / 1000,
        duration: Math.round(selectedDuration * 1000) / 1000,
      };
      console.log("[VideoTrimmer] Confirming trim selection:", trimData);
      onConfirm(trimData);
    }
  };

  return (
    <div className="video-trimmer">
      <div className="trimmer-header">
        <h3>Select Video Segment</h3>
        <p className="trimmer-subtitle">
          Select the segment to analyze (up to {Math.floor(maxDuration / 60)} minutes)
        </p>
      </div>

      <div className="video-preview">
        {videoUrl && (
          <video
            ref={videoRef}
            src={videoUrl}
            onLoadedMetadata={handleLoadedMetadata}
            onDurationChange={handleDurationChange}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            preload="metadata"
          />
        )}
        <button className="play-btn" onClick={togglePlay}>
          {isPlaying ? "⏸" : "▶"}
        </button>
      </div>

      <div className="timeline-container">
        <div className="timeline">
          {/* Background track */}
          <div className="timeline-track" />
          
          {/* Selected range highlight */}
          <div
            className="timeline-selection"
            style={{
              left: `${(startTime / duration) * 100}%`,
              width: `${((endTime - startTime) / duration) * 100}%`,
            }}
          />
          
          {/* Current playhead */}
          <div
            className="timeline-playhead"
            style={{ left: `${(currentTime / duration) * 100}%` }}
          />
          
          {/* Start handle */}
          <input
            type="range"
            className="timeline-handle start-handle"
            min={0}
            max={duration}
            step={0.1}
            value={startTime}
            onChange={handleStartChange}
          />
          
          {/* End handle */}
          <input
            type="range"
            className="timeline-handle end-handle"
            min={0}
            max={duration}
            step={0.1}
            value={endTime}
            onChange={handleEndChange}
          />
        </div>

        <div className="timeline-labels">
          <span>{formatTime(0)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      <div className="trim-info">
        <div className="time-inputs">
          <div className="time-input">
            <label>Start</label>
            <span className="time-value">{formatTime(startTime)}</span>
          </div>
          <div className="time-input">
            <label>End</label>
            <span className="time-value">{formatTime(endTime)}</span>
          </div>
          <div className="time-input">
            <label>Duration</label>
            <span className={`time-value ${!isValidSelection ? "invalid" : ""}`}>
              {formatTime(selectedDuration)}
            </span>
          </div>
        </div>
        
        {selectedDuration > maxDuration && (
          <p className="trim-warning">
            ⚠️ Selection exceeds {maxDuration}s limit. Adjust the range.
          </p>
        )}
      </div>

      <div className="trimmer-actions">
        <button className="btn-cancel" onClick={onCancel}>
          Cancel
        </button>
        <button
          className="btn-confirm"
          onClick={handleConfirm}
          disabled={!isValidSelection}
        >
          Analyze Selected Segment
        </button>
      </div>
    </div>
  );
}

export default VideoTrimmer;

