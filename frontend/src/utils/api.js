import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const rawBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
const normalizedBaseUrl = rawBaseUrl.replace(/\/+$/, "");

const api = axios.create({
  baseURL: normalizedBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add X-User-ID header
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const userId = authStore.user?.user_id || authStore.user?.id;
    if (userId) {
      config.headers["X-User-ID"] = userId;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      const authStore = useAuthStore();
      authStore.logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// API Call wrapper function for backward compatibility
export async function apiCall(url, method = "GET", data = null) {
  try {
    let response;
    
    if (method === "GET") {
      response = await api.get(url);
    } else if (method === "POST") {
      response = await api.post(url, data);
    } else if (method === "PUT") {
      response = await api.put(url, data);
    } else if (method === "DELETE") {
      response = await api.delete(url);
    } else if (method === "PATCH") {
      response = await api.patch(url, data);
    }
    
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || "API error";
    throw new Error(errorMessage);
  }
}

export default api;