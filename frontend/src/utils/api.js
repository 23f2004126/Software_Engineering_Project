import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// API Call wrapper function
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