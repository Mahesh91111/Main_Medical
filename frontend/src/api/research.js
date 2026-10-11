import api from "./client";

export async function searchMedicalResearch(query) {
  const response = await api.post("/research/query", {
    query: query.trim(),
  });

  return response.data;
}