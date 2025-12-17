import { useEffect, useState, useCallback } from "react";
import { apiClient } from "../services/api";

/**
 * Fetches and normalizes biomechanical metrics for a selected video.
 * Now supports manual refetch after processing completes.
 */
export function useVideoMetrics(videoId) {
  const [metrics, setMetrics] = useState({});
  const [narrative, setNarrative] = useState({});
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    if (!videoId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(`/metrics/${videoId}`);
      setMetrics(response.data.metrics ?? {});
      setNarrative(response.data.narrative ?? {});
    } catch (err) {
      // Don't set error if metrics just aren't ready yet (404)
      if (err.response?.status !== 404) {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [videoId]);

  useEffect(() => {
    if (!videoId) return;
    fetchMetrics();
  }, [videoId, fetchMetrics]);

  return { metrics, narrative, isLoading, error, refetch: fetchMetrics };
}

