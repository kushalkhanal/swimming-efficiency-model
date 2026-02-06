import { useState, useEffect, useCallback, useMemo } from "react";
import { apiClient } from "../services/api";
import { formatKeypointsFromAPI } from "../utils/keypointsFormatter";

/**
 * Hook to fetch and format all keypoints for swim analysis.
 * Returns keypoints in the format: { frameNumber: { keypointName: { x, y, z, confidence } } }
 */
export function useFormattedKeypoints(videoId) {
  const [keypointsData, setKeypointsData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAllKeypoints = useCallback(async () => {
    if (!videoId) {
      setKeypointsData({});
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch all keypoints in batches
      let allFrames = [];
      let start = 0;
      const limit = 500;
      let hasMore = true;

      while (hasMore) {
        const response = await apiClient.get(`/keypoints/${videoId}`, {
          params: { start, limit }
        });
        
        const frames = response.data.frames || [];
        allFrames = allFrames.concat(frames);
        
        hasMore = frames.length === limit;
        start += limit;
      }

      // Format keypoints
      const formatted = formatKeypointsFromAPI({ frames: allFrames });
      setKeypointsData(formatted);
    } catch (err) {
      console.error("Failed to fetch keypoints:", err);
      setError(err);
      setKeypointsData({});
    } finally {
      setIsLoading(false);
    }
  }, [videoId]);

  useEffect(() => {
    fetchAllKeypoints();
  }, [fetchAllKeypoints]);

  return {
    keypointsData,
    isLoading,
    error,
    refetch: fetchAllKeypoints,
  };
}

