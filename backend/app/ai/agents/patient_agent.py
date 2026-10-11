
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.llm import get_llm
from app.services.clinical_service import get_patient_records


PATIENT_AGENT_PROMPT = """
You are a clinical-record assistant for authorized clinical users.

Answer the user's question using only the supplied patient records.
Do not invent findings or assume missing information.
Do not diagnose or prescribe treatment.
If the records do not answer the question, say what is missing.
Preserve units and dates exactly as recorded where possible.
Clearly distinguish recorded interpretations from your own explanation.
A qualified clinician must review clinical decisions.
"""


def run_patient_agent(state: dict) -> dict:
    patient_id = state.get("patient_id")

    if not patient_id:
        return {
            "answer": (
                "Please provide a patient ID to retrieve an authorized "
                "patient's records."
            ),
            "citations": [],
        }

    records = get_patient_records(
        db=state["db"],
        user=state["user"],
        patient_id=patient_id,
    )

    response = get_llm().invoke(
        [
            SystemMessage(content=PATIENT_AGENT_PROMPT),
            HumanMessage(
                content=(
                    f"Question: {state['question']}\n\n"
                    "Patient records:\n"
                    + json.dumps(records, ensure_ascii=False, default=str)
                )
            ),
        ]
    )

    return {
        "answer": response.content,
        "citations": [],
        "patient_records": records,
    }
