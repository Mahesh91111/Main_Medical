
from uuid import UUID

from langchain_core.output_parsers import StrOutputParser

from app.ai.llm import get_llm
from app.ai.prompts import MEDICAL_RAG_PROMPT
from app.ai.retriever import retrieve_documents
from app.models.user import User
from app.schemas.assistant import (
    AssistantResponse,
    SourceCitation,
)


def format_context(documents: list[dict]) -> str:
    """Format retrieved chunks and assign source identifiers."""

    sections = []

    for index, document in enumerate(documents, start=1):
        sections.append(
            f"[S{index}]\n"
            f"Document: {document.get('filename') or 'Unknown'}\n"
            f"Page: {document.get('page_number') or 'Unknown'}\n"
            f"Content:\n{document['text']}"
        )

    return (
        "\n\n---\n\n".join(sections)
        if sections
        else "No relevant document evidence was retrieved."
    )


def build_citations(
    documents: list[dict],
) -> list[SourceCitation]:
    """Convert retrieved source metadata into API citations."""

    citations = []

    for document in documents:
        raw_id = document.get("document_id")

        try:
            document_id = UUID(str(raw_id)) if raw_id else None
        except (ValueError, TypeError):
            document_id = None

        raw_page = document.get("page_number")

        try:
            page_number = int(raw_page) if raw_page is not None else None
            if page_number is not None and page_number < 1:
                page_number = None
        except (ValueError, TypeError):
            page_number = None

        citations.append(
            SourceCitation(
                document_id=document_id,
                filename=document.get("filename"),
                page_number=page_number,
                excerpt=document["text"][:2000],
                score=document.get("score"),
            )
        )

    return citations


def answer_question(
    question: str,
    user: User,
    patient_id: UUID | None = None,
    top_k: int = 5,
) -> AssistantResponse:
    """Retrieve evidence and generate a grounded answer."""

    documents = retrieve_documents(
        question=question,
        user=user,
        patient_id=patient_id,
        top_k=top_k,
    )

    if not documents:
        return AssistantResponse(
            answer=(
                "I could not find relevant evidence in the accessible "
                "documents. Please provide a relevant document or consult "
                "a qualified healthcare professional."
            ),
            citations=[],
        )

    context = format_context(documents)

    chain = MEDICAL_RAG_PROMPT | get_llm() | StrOutputParser()

    answer = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return AssistantResponse(
        answer=answer.strip(),
        citations=build_citations(documents),
    )
