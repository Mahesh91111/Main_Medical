
import api from "./client";

export async function getPatients(params = {}) {
  const response = await api.get("/patients", { params });
  const data = response.data;

  // Support common list and pagination response formats.
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.patients)) return data.patients;
  if (Array.isArray(data?.results)) return data.results;

  return [];
}

export async function getPatientById(patientId) {
  const response = await api.get(
    `/patients/${encodeURIComponent(patientId)}`
  );

  return response.data;
}

export async function createPatient(patientData) {
  const response = await api.post("/patients", patientData);
  return response.data;
}
