
import api from "./client";

export async function loginUser(credentials) {
  const response = await api.post("/auth/login", {
    email: credentials.email,
    password: credentials.password
  });

  return response.data;
}

export async function registerUser(details) {
  const response = await api.post("/auth/register", {
    email: details.email,
    full_name: details.full_name,
    password: details.password
  });

  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/auth/me");
  return response.data;
}
