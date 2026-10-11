
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.llm import get_llm
from app.services.clinical_service import get_patient_records


SUMMARY_SYSTEM_PROMPT = """
You are a clinical-record summarization assistant.

Summarize only the supplied patient-record data.
Do not invent facts, dates, diagnoses, medication instructions, or lab results.
Clearly distinguish recorded facts from missing information.
Mention abnormal lab interpretations only when supplied in the records.
Do not recommend starting, stopping, or changing medication.
Do not present this summary as a diagnosis or a substitute for clinician review.
Use clear headings:
1. Patient context
2. Encounter history
3. Lab results
4. Recorded medications
5. Missing information and review points
"""


def run_summary(state: dict) -> dict:
    patient_id = state.get("patient_id")

    if not patient_id:
        return {
            "answer": (
                "Please provide an authorized patient ID to summarize "
                "the patient's clinical records."
            ),
            "citations": [],
        }

    records = get_patient_records(
        db=state["db"],
        user=state["user"],
        patient_id=patient_id,
    )

    llm = get_llm()
    response = llm.invoke(
        [
            SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "User's request:\n"
                    f"{state['question']}\n\n"
                    "Authorized clinical records (JSON):\n"
                    f"{json.dumps(records, ensure_ascii=False, default=str)}"
                )
            ),
        ]
    )

    return {
        "answer": response.content,
        "citations": [],
        "patient_records": records,
    }
