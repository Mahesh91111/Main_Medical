
from types import SimpleNamespace
from uuid import uuid4

import app.ai.agents.medical_rag_agent as medical_rag_agent

from app.ai.graph import run_medical_assistant


def test_graph_executes_medical_rag_route(monkeypatch):
    def fake_answer_question(
        question,
        user,
        patient_id=None,
    ):
        return SimpleNamespace(
            answer="Mocked medical evidence answer.",
            citations=[],
        )

    monkeypatch.setattr(
        medical_rag_agent,
        "answer_question",
        fake_answer_question,
    )

    user = SimpleNamespace(
        id=uuid4(),
        role="clinician",
    )

    result = run_medical_assistant(
        question="What is hypertension?",
        user=user,
        db=None,
    )

    assert result["route"] == "medical_rag"
    assert result["answer"] == "Mocked medical evidence answer."
    assert result["citations"] == []


def test_graph_rejects_researcher_patient_summary():
    researcher = SimpleNamespace(
        id=uuid4(),
        role="researcher",
    )

    result = run_medical_assistant(
        question="Summarize patient records",
        user=researcher,
        db=None,
    )

    assert result["route"] == "clarify"
    assert result["answer"]
