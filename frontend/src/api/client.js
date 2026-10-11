import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  headers: {
    Accept: "application/json"
  },
  timeout: 30000
});

export const TOKEN_KEY = "medical_access_token";

// The login token lives in sessionStorage, so it is cleared when the
// browser tab is closed. Opening the app again shows the register/login pages.
// Any token left in localStorage by the old version is removed.
localStorage.removeItem(TOKEN_KEY);

api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem(TOKEN_KEY);

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const isLoginRequest = error.config?.url?.includes("/auth/login");

    if (status === 401 && !isLoginRequest) {
      sessionStorage.removeItem(TOKEN_KEY);

      window.dispatchEvent(new Event("auth:unauthorized"));
    }

    return Promise.reject(error);
  }
);

export default api;
