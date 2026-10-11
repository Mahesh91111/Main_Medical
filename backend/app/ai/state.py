
from typing import Any, Literal, TypedDict


AgentName = Literal[
    "patient",
    "medical_rag",
    "summary",
    "research",
    "clarify",
]


class MedicalAssistantState(TypedDict, total=False):
    question: str
    user: Any
    db: Any

    # Optional patient context supplied by the authenticated request.
    patient_id: str | None

    # Set by the supervisor.
    route: AgentName

    # Internal context assembled by agents.
    patient_records: dict[str, Any]
    answer: str
    citations: list[dict[str, Any]]
    errors: list[str]
