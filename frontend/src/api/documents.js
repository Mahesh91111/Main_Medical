import api from "./client";

export async function getDocuments(params = {}) {
  const response = await api.get("/documents", { params });
  const data = response.data;

  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.documents)) return data.documents;
  if (Array.isArray(data?.results)) return data.results;

  return [];
}

export async function deleteDocument(documentId) {
  await api.delete(`/documents/${encodeURIComponent(documentId)}`);
}

export async function uploadDocument(
  file,
  patientId,
  onUploadProgress,
  signal
) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post("/documents/upload", formData, {
    // The backend reads patient_id from the URL query, not the form body.
    params: patientId ? { patient_id: String(patientId) } : undefined,
    // Lets the user cancel an upload that is in progress.
    signal,
    // The server answers as soon as the file is saved; processing happens afterwards.
    timeout: 120000,
    onUploadProgress: (event) => {
      if (event.total && onUploadProgress) {
        const percent = Math.round((event.loaded * 100) / event.total);
        onUploadProgress(percent);
      }
    }
  });

  return response.data;
}
