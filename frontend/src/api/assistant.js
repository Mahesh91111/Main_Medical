
import api from "./client";

export async function askMedicalAssistant({
  question,
  patientId = null,
}) {
  const response = await api.post("/assistant/ask", {
    question: question.trim(),
    patient_id: patientId || null,
  });

  return response.data;
}