
from app.ai.rag_chain import answer_question


RESEARCH_PREFIX = """
Research task: Answer the user's question using the retrieved medical
document evidence. Prefer careful, evidence-grounded explanations.
Identify limitations and uncertainty. Do not invent papers, authors,
DOIs, trial results, or citations. If the supplied evidence is insufficient,
say so clearly. This output is for research support, not medical advice.

User question:
"""


def run_research(state: dict) -> dict:
    result = answer_question(
        question=RESEARCH_PREFIX + state["question"],
        user=state["user"],
        patient_id=None,
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
