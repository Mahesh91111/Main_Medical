
from langgraph.graph import END, START, StateGraph

from app.ai.state import MedicalAssistantState
from app.ai.agents.patient_agent import run_patient_agent
from app.ai.agents.medical_rag_agent import run_medical_rag
from app.ai.agents.summary_agent import run_summary
from app.ai.agents.research_agent import run_research


CLINICAL_ROLES = {"admin", "clinician"}
ALL_SUPPORTED_ROLES = {"admin", "clinician", "researcher"}


def supervisor_node(state: MedicalAssistantState) -> dict:
    """
    Explicit intent routing. Authorization is still checked separately
    inside the relevant tools and API endpoint.
    """
    question = state["question"].strip().lower()
    user = state["user"]

    if user.role not in ALL_SUPPORTED_ROLES:
        return {
            "route": "clarify",
            "answer": "Your account does not have permission to use this assistant.",
            "citations": [],
        }

    if any(
        term in question
        for term in (
            "summarize patient",
            "summarise patient",
            "clinical summary",
            "patient summary",
            "summarize records",
            "summarise records",
            "record summary",
        )
    ):
        route = "summary"

    elif any(
        term in question
        for term in (
            "patient record",
            "patient records",
            "patient history",
            "encounter",
            "lab result",
            "lab results",
            "medication",
            "medications",
            "patient details",
        )
    ):
        route = "patient"

    elif any(
        term in question
        for term in (
            "research",
            "clinical trial",
            "systematic review",
            "research paper",
            "literature review",
            "study evidence",
        )
    ):
        route = "research"

    else:
        route = "medical_rag"

    # Researchers cannot use patient-record workflows.
    if route in {"patient", "summary"} and user.role not in CLINICAL_ROLES:
        return {
            "route": "clarify",
            "answer": (
                "This request requires an authorized clinical role. "
                "Please ask a general medical-knowledge question instead."
            ),
            "citations": [],
        }

    return {"route": route}


def patient_node(state: MedicalAssistantState) -> dict:
    return run_patient_agent(state)


def medical_rag_node(state: MedicalAssistantState) -> dict:
    return run_medical_rag(state)


def summary_node(state: MedicalAssistantState) -> dict:
    return run_summary(state)


def research_node(state: MedicalAssistantState) -> dict:
    return run_research(state)


def route_after_supervisor(state: MedicalAssistantState) -> str:
    return state.get("route", "clarify")


def error_node(state: MedicalAssistantState) -> dict:
    return {
        "answer": (
            "I could not safely complete this request. Please check the "
            "request and your access permissions, then try again."
        ),
        "citations": [],
    }


def build_medical_graph():
    workflow = StateGraph(MedicalAssistantState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("patient", patient_node)
    workflow.add_node("medical_rag", medical_rag_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("research", research_node)
    workflow.add_node("clarify", error_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "patient": "patient",
            "medical_rag": "medical_rag",
            "summary": "summary",
            "research": "research",
            "clarify": "clarify",
        },
    )

    for node_name in (
        "patient",
        "medical_rag",
        "summary",
        "research",
        "clarify",
    ):
        workflow.add_edge(node_name, END)

    return workflow.compile()


medical_assistant_graph = build_medical_graph()


def run_medical_assistant(
    question: str,
    user,
    db,
    patient_id: str | None = None,
) -> dict:
    initial_state: MedicalAssistantState = {
        "question": question,
        "user": user,
        "db": db,
        "patient_id": patient_id,
        "route": "clarify",
        "answer": "",
        "citations": [],
        "errors": [],
    }

    result = medical_assistant_graph.invoke(initial_state)

    return {
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "route": result.get("route", "clarify"),
    }
