import { useState, useEffect, useCallback } from "react";
import { apiClient } from "../services/api";

/**
 * Hook to fetch keypoints for 3D pose visualization.
 */
export function useKeypoints(videoId) {
  const [keypoints, setKeypoints] = useState([]);
  const [currentKeypoints, setCurrentKeypoints] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all keypoints for a video
  const fetchKeypoints = useCallback(async () => {
    if (!videoId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get(`/keypoints/${videoId}`, {
        params: { limit: 500 }
      });
      
      const frames = response.data.frames || [];
      setKeypoints(frames);
      
      // Set initial keypoints to first frame
      if (frames.length > 0) {
        setCurrentKeypoints(frames[0].keypoints);
      }
    } catch (err) {
      console.error("Failed to fetch keypoints:", err);
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [videoId]);

  // Fetch keypoints when video ID changes
  useEffect(() => {
    if (videoId) {
      fetchKeypoints();
    } else {
      setKeypoints([]);
      setCurrentKeypoints(null);
    }
  }, [videoId, fetchKeypoints]);

  // Update current keypoints based on frame index
  const setFrameIndex = useCallback((frameIndex) => {
    if (!keypoints.length) return;
    
    // Find closest frame
    const frame = keypoints.find(f => f.frame_index === frameIndex) ||
                  keypoints.reduce((prev, curr) => 
                    Math.abs(curr.frame_index - frameIndex) < Math.abs(prev.frame_index - frameIndex) 
                      ? curr : prev
                  );
    
    if (frame) {
      setCurrentKeypoints(frame.keypoints);
    }
  }, [keypoints]);

  return {
    keypoints,
    currentKeypoints,
    isLoading,
    error,
    setFrameIndex,
    refetch: fetchKeypoints,
  };
}

