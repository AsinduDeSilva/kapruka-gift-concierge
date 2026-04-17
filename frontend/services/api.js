import axios from "axios";

const API_BASE = "http://localhost:8000";

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const signUp = (email, password) =>
  api.post("/auth/signup", { email, password });

export const signIn = (email, password) => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return api.post("/auth/signin", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const createSession = () => api.get("/chat/session");

export const getProfile = () => api.get("/chat/profile");

export const sendMessageStream = async (sessionId, userQuery, onStatus, onComplete, onError) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ session_id: sessionId, user_query: userQuery })
    });

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
        return;
      }
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); 
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const dataStr = line.slice(6);
            const data = JSON.parse(dataStr);
            if (data.status && onStatus) onStatus(data.status);
            if (data.final && onComplete) onComplete(data.final, data.profile);
            if (data.error && onError) onError(new Error(data.error));
          } catch (e) {
            console.error("Error parsing SSE data line", e);
          }
        }
      }
    }
  } catch (err) {
    if (onError) onError(err);
  }
};

