
from types import SimpleNamespace
from uuid import uuid4

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

import app.ai.rag_chain as rag_chain


def test_rag_returns_no_evidence_message(monkeypatch):
    monkeypatch.setattr(
        rag_chain,
        "retrieve_documents",
        lambda **kwargs: [],
    )

    user = SimpleNamespace(id=uuid4(), role="clinician")

    result = rag_chain.answer_question(
        question="What does the document say?",
        user=user,
    )

    assert result.answer
    assert result.citations == []


def test_rag_uses_retrieved_evidence(monkeypatch):
    fake_document = {
        "document_id": str(uuid4()),
        "filename": "synthetic-guide.pdf",
        "page_number": 1,
        "chunk_index": 0,
        "text": "Synthetic evidence: example content for testing.",
        "score": 0.95,
    }

    monkeypatch.setattr(
        rag_chain,
        "retrieve_documents",
        lambda **kwargs: [fake_document],
    )

    fake_llm = RunnableLambda(
        lambda _: AIMessage(
            content="The retrieved document contains example evidence [S1]."
        )
    )

    monkeypatch.setattr(
        rag_chain,
        "get_llm",
        lambda: fake_llm,
    )

    user = SimpleNamespace(id=uuid4(), role="clinician")

    result = rag_chain.answer_question(
        question="Summarize the evidence in this document.",
        user=user,
    )

    assert "example evidence" in result.answer
    assert len(result.citations) >= 1
    assert result.citations[0].filename == "synthetic-guide.pdf"
