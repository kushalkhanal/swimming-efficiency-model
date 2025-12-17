import { useState } from "react";
import { apiClient, uploadClient } from "../services/api";

/**
 * Manages frame overlays and export interactions with the backend.
 */
export function useFrameData(videoId) {
  const [frameOverlay, setFrameOverlay] = useState(null);
  const [totalFrames, setTotalFrames] = useState(0);
  const [uploadError, setUploadError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const uploadVideo = async (file, onUploaded, onProgress, trimSettings = null) => {
    if (!file) {
      setUploadError("No file selected");
      return;
    }

    // Validate file type
    if (!file.type.startsWith("video/")) {
      setUploadError("Please select a valid video file");
      return;
    }

    // Validate file size (e.g., max 500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      setUploadError("File size too large. Maximum size is 500MB");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      console.log("Uploading video:", file.name, "Size:", file.size);
      if (trimSettings) {
        console.log("Trim settings:", trimSettings);
      }

      const response = await uploadClient.post("/upload-video", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 300000, // 5 minutes timeout for large files
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percent = (progressEvent.loaded / progressEvent.total) * 100;
            onProgress(percent);
          }
        },
      });

      if (!response.data || !response.data.video_id) {
        throw new Error("Invalid response from server");
      }

      const newVideoId = response.data.video_id;
      console.log("Video uploaded successfully. Video ID:", newVideoId);
      onUploaded(newVideoId);

      // Build processing payload with trim settings
      const processPayload = { video_id: newVideoId };
      if (trimSettings) {
        processPayload.start_time = trimSettings.startTime;
        processPayload.end_time = trimSettings.endTime;
      }

      // Kick off processing (don't wait for it to complete)
      apiClient.post("/process-video", processPayload)
        .then(() => {
          console.log("Video processing started with settings:", processPayload);
        })
        .catch((err) => {
          console.error("Failed to start video processing:", err);
          setUploadError("Upload succeeded but processing failed to start");
        });

      // Placeholder visual overlay until backend returns real frames.
      setFrameOverlay({
        videoSrc: URL.createObjectURL(file),
        frameRate: 30,
        keypoints: Array.from({ length: 33 }, () => [Math.random(), Math.random()])
      });
      setTotalFrames(900);
    } catch (error) {
      console.error("Upload error:", error);
      if (error.response) {
        // Server responded with error status
        setUploadError(error.response.data?.error || `Upload failed: ${error.response.status} ${error.response.statusText}`);
      } else if (error.request) {
        // Request made but no response
        setUploadError("Could not connect to server. Make sure the backend is running.");
      } else {
        // Something else happened
        setUploadError(error.message || "Upload failed. Please try again.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const fetchFrameOverlay = async (frameId) => {
    const response = await apiClient.get(`/video-frame/${frameId}`, {
      responseType: "arraybuffer"
    });
    const blob = new Blob([response.data], { type: "image/jpeg" });
    return URL.createObjectURL(blob);
  };

  const exportReport = async (vid, format) => {
    if (!vid) return;
    const response = await apiClient.get(`/reports/${vid}`, {
      params: { format },
      responseType: "blob"
    });
    const url = URL.createObjectURL(response.data);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `swim-report-${vid}.${format}`;
    anchor.click();
  };

  return {
    frameOverlay,
    totalFrames,
    uploadVideo,
    fetchFrameOverlay,
    exportReport,
    uploadError,
    isUploading,
    clearError: () => setUploadError(null)
  };
}

