
from types import SimpleNamespace

from app.ai.graph import supervisor_node


def test_patient_api_requires_authentication(client):
    response = client.get("/api/v1/patients")

    assert response.status_code in (401, 403)


def test_researcher_cannot_use_patient_summary_route():
    researcher = SimpleNamespace(role="researcher")

    result = supervisor_node({
        "question": "Summarize patient records",
        "user": researcher,
    })

    assert result["route"] == "clarify"
    assert "answer" in result


def test_clinician_can_route_patient_summary():
    clinician = SimpleNamespace(role="clinician")

    result = supervisor_node({
        "question": "Summarize patient records",
        "user": clinician,
    })

    assert result["route"] == "summary"


def test_researcher_can_route_research_questions():
    researcher = SimpleNamespace(role="researcher")

    result = supervisor_node({
        "question": "Explain evidence from clinical trials",
        "user": researcher,
    })

    assert result["route"] == "research"
