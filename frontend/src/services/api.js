import axios from "axios";

const BASE_URL = "/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

export const uploadClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "multipart/form-data"
  }
});

// Axios interceptors could be added here for error handling or logging.

