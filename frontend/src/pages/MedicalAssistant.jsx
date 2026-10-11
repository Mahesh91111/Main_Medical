import { useEffect, useRef, useState } from "react";
import {
  Bot,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserRound,
} from "lucide-react";

import { askMedicalAssistant } from "../api/assistant";
import { getPatients } from "../api/patients";
import ChatMessage from "../components/assistant/ChatMessage";
import ChatComposer from "../components/assistant/ChatComposer";

function getErrorMessage(error) {
  if (error.response?.status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (error.response?.status === 403) {
    return "You do not have permission to use this assistant.";
  }

  if (error.response?.status === 422) {
    return (
      error.response?.data?.detail ||
      "The backend rejected the request. Check the request schema."
    );
  }

  if (!error.response) {
    return "Cannot reach the backend. Check that FastAPI is running.";
  }

  return (
    error.response?.data?.detail ||
    error.response?.data?.message ||
    "The assistant could not complete your request. Please try again."
  );
}

function getAnswer(data) {
  const answer =
    data?.answer ??
    data?.response ??
    data?.output ??
    data?.message;

  if (typeof answer === "string" && answer.trim()) {
    return answer;
  }

  return "The backend returned no answer. Please try again.";
}

function getCitations(data) {
  const citations =
    data?.citations ??
    data?.sources ??
    data?.references ??
    [];

  return Array.isArray(citations) ? citations : [];
}

export default function MedicalAssistant() {
  const [question, setQuestion] = useState("");
  const [patientId, setPatientId] = useState("");
  const [patients, setPatients] = useState([]);
  const [patientLoading, setPatientLoading] = useState(true);
  const [patientError, setPatientError] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const conversationEndRef = useRef(null);

  useEffect(() => {
    let active = true;

    async function loadPatients() {
      try {
        setPatientError("");
        const data = await getPatients();

        if (active) setPatients(data);
      } catch {
        if (active) {
          setPatientError(
            "Patient context could not be loaded. You can still ask a general question."
          );
        }
      } finally {
        if (active) setPatientLoading(false);
      }
    }

    loadPatients();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  async function handleAsk() {
    const currentQuestion = question.trim();

    if (!currentQuestion || loading) return;

    const userMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: currentQuestion,
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const data = await askMedicalAssistant({
        question: currentQuestion,
        patientId: patientId || null,
      });

      const assistantMessage = {
        id: `${Date.now()}-assistant`,
        role: "assistant",
        content: getAnswer(data),
        citations: getCitations(data),
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    if (loading) return;

    setMessages([]);
    setQuestion("");
    setError("");
  }

  const selectedPatient = patients.find(
    (patient) =>
      String(patient.id ?? patient.patient_id) === patientId
  );

  return (
    <div className="workspace-page assistant-page">
      <div className="workspace-page-heading assistant-heading">
        <div>
          <div className="eyebrow">
            <Sparkles size={14} /> CLINICAL INTELLIGENCE
          </div>

          <h1>AI Medical Assistant</h1>

          <p>
            Ask clinical information questions and explore
            supporting documents with optional patient context.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={startNewChat}
          disabled={loading}
        >
          New conversation
        </button>
      </div>

      <div className="assistant-context-bar">
        <div className="assistant-context-label">
          <UserRound size={17} />
          <div>
            <strong>Patient context</strong>
            <span>Optional · Select only when authorized</span>
          </div>
        </div>

        <div className="assistant-patient-select">
          <select
            value={patientId}
            onChange={(event) => setPatientId(event.target.value)}
            disabled={patientLoading || loading}
            aria-label="Select patient context"
          >
            <option value="">
              {patientLoading
                ? "Loading patients..."
                : "General question — no patient selected"}
            </option>

            {patients.map((patient) => {
              const id = patient.id ?? patient.patient_id;

              return (
                <option key={id} value={String(id)}>
                  {[
                    patient.first_name,
                    patient.last_name,
                  ]
                    .filter(Boolean)
                    .join(" ") || `Patient ${id}`}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {patientError && (
        <div className="assistant-inline-warning" role="status">
          {patientError}
        </div>
      )}

      {selectedPatient && (
        <div className="selected-patient-banner">
          <Stethoscope size={16} />
          <span>
            Context selected:{" "}
            <strong>
              {[
                selectedPatient.first_name,
                selectedPatient.last_name,
              ]
                .filter(Boolean)
                .join(" ") || `Patient ${patientId}`}
            </strong>
          </span>
          <span className="context-notice">
            The backend must enforce access permissions.
          </span>
        </div>
      )}

      <section className="assistant-chat-panel">
        <div className="assistant-chat-header">
          <div className="assistant-bot-icon">
            <Bot size={20} />
          </div>

          <div>
            <strong>Clinica AI</strong>
            <span>
              {loading
                ? "Preparing a response..."
                : "Medical information assistant"}
            </span>
          </div>

          <span className="assistant-status">
            <span className="status-dot" />
            Ready
          </span>
        </div>

        <div
          className="assistant-conversation"
          aria-live="polite"
          aria-busy={loading}
        >
          {messages.length === 0 && (
            <div className="assistant-empty-state">
              <div className="assistant-empty-icon">
                <Sparkles size={25} />
              </div>

              <h2>How can I help you today?</h2>

              <p>
                Ask about medical literature, document contents,
                or clinical concepts supported by your backend.
              </p>

              <div className="assistant-suggestions">
                {[
                  "Summarize the key findings in the available medical documents.",
                  "Explain the difference between sensitivity and specificity.",
                  "What evidence supports this treatment approach?",
                ].map((suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    onClick={() => setQuestion(suggestion)}
                    disabled={loading}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
            />
          ))}

          {loading && (
            <div className="assistant-thinking" role="status">
              <span className="thinking-dots">
                <span />
                <span />
                <span />
              </span>
              <span>Analyzing your question...</span>
            </div>
          )}

          {error && (
            <div className="assistant-error" role="alert">
              <strong>Unable to get a response</strong>
              <p>{error}</p>
              <button
                type="button"
                onClick={() => {
                  const lastUserMessage = [...messages]
                    .reverse()
                    .find((message) => message.role === "user");

                  if (lastUserMessage) {
                    setQuestion(lastUserMessage.content);
                  }
                }}
              >
                Restore last question
              </button>
            </div>
          )}

          <div ref={conversationEndRef} />
        </div>

        <ChatComposer
          value={question}
          onChange={setQuestion}
          onSubmit={handleAsk}
          loading={loading}
        />

        <div className="assistant-disclaimer">
          <ShieldCheck size={15} />
          AI-generated information can be incomplete or incorrect.
          Verify important findings with authoritative sources and
          qualified healthcare professionals.
        </div>
      </section>
    </div>
  );
}