import { useState, useEffect, useCallback, useRef } from "react";
import { io } from "socket.io-client";

/**
 * Hook for real-time video processing progress via WebSocket
 */
export function useProcessingProgress() {
  const [progress, setProgress] = useState({
    stage: null,
    progress: 0,
    message: "",
    isProcessing: false,
    videoId: null,
  });
  
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket server
    const socket = io(window.location.origin, {
      path: "/socket.io",
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("WebSocket connected");
    });

    socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
    });

    socket.on("processing_progress", (data) => {
      setProgress({
        stage: data.stage,
        progress: data.progress,
        message: data.message,
        isProcessing: data.progress < 100,
        videoId: data.video_id,
      });

      // Auto-clear after completion
      if (data.progress >= 100) {
        reconnectTimeoutRef.current = setTimeout(() => {
          setProgress((prev) => ({
            ...prev,
            isProcessing: false,
          }));
        }, 2000);
      }
    });

    socket.on("connect_error", (error) => {
      console.warn("WebSocket connection error:", error.message);
    });

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      socket.disconnect();
    };
  }, []);

  const startProcessing = useCallback((videoId) => {
    setProgress({
      stage: "upload",
      progress: 0,
      message: "Starting upload...",
      isProcessing: true,
      videoId,
    });
  }, []);

  const setUploadProgress = useCallback((percent) => {
    setProgress((prev) => ({
      ...prev,
      stage: "upload",
      progress: Math.min(percent * 0.05, 5), // Upload is 0-5% of total
      message: `Uploading... ${Math.round(percent)}%`,
    }));
  }, []);

  const resetProgress = useCallback(() => {
    setProgress({
      stage: null,
      progress: 0,
      message: "",
      isProcessing: false,
      videoId: null,
    });
  }, []);

  return {
    ...progress,
    startProcessing,
    setUploadProgress,
    resetProgress,
  };
}

