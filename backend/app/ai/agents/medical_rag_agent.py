
from app.ai.rag_chain import answer_question


def run_medical_rag(state: dict) -> dict:
    user = state["user"]
    question = state["question"]

    result = answer_question(
        question=question,
        user=user,
        patient_id=state.get("patient_id"),
    )

    return {
        "answer": result.answer,
        "citations": [
            citation.model_dump(mode="json")
            if hasattr(citation, "model_dump")
            else citation
            for citation in result.citations
        ],
    }
