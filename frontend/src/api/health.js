import axios from "axios";

const healthClient = axios.create({
  baseURL: "",
  timeout: 5000,
});

export async function checkBackendHealth() {
  try {
    const response = await healthClient.get("/health/live");

    return {
      online: true,
      status: response.data?.status || "healthy",
      message: "Backend is reachable.",
    };
  } catch (error) {
    return {
      online: false,
      status: "unavailable",
      message: error.response
        ? `Health check failed with HTTP ${error.response.status}.`
        : "Backend is unavailable. Check that FastAPI is running.",
    };
  }
}
