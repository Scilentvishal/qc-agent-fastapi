# app/api/sops.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.rag_service import answer_sop_question

router = APIRouter(prefix="/sops", tags=["SOP Knowledge & RAG"])


class SOPQuestionRequest(BaseModel):
    question: str = Field(
        ...,
        description="Question regarding pharmaceutical manufacturing or QC release rules",
        examples=["What are the pH limits for oral solution release?"]
    )


@router.post("/ask")
def ask_sop_endpoint(payload: SOPQuestionRequest) -> dict:
    """
    Asks a question against indexed SOP documents.
    Retrieves evidence from Qdrant and generates a grounded response with citations.
    """
    result = answer_sop_question(payload.question)
    return {
        "question": payload.question,
        "result": result
    }