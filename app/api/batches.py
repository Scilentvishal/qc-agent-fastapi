# app/api/batches.py
from app.services.llm_service import explain_qc_findings_with_llm
from fastapi import APIRouter, HTTPException, status
from app.schemas.schemas import BatchValidationRequest
from app.services import batch_service

# Router with prefix and tags
router = APIRouter(prefix="/batches", tags=["Batches"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_batch(payload: BatchValidationRequest) -> dict:
    """Create and store a sample QC batch record."""
    record = batch_service.create_new_batch(payload.model_dump())
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch '{payload.batch_id}' already exists."
        )
    return {
        "message": "Batch record created successfully",
        "batch_id": payload.batch_id,
        "record": record
    }


@router.get("")
def list_batches(limit: int = 10, skip: int = 0) -> dict:
    """List stored batch records with pagination."""
    batches = batch_service.get_all_batches(skip=skip, limit=limit)
    return {
        "total_count": len(batches),
        "limit": limit,
        "skip": skip,
        "batches": batches
    }


@router.get("/{batch_id}")
def get_batch(batch_id: str) -> dict:
    """Retrieve a single batch record by ID."""
    batch = batch_service.get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found."
        )
    return batch


@router.post("/{batch_id}/validate")
def validate_batch(batch_id: str) -> dict:
    """Run deterministic QC validation against a stored batch."""
    report = batch_service.validate_existing_batch(batch_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found."
        )
    return {
        "batch_id": batch_id,
        "is_approved": report["is_approved"],
        "audit_report": report
    }


@router.post("/{batch_id}/explain-findings", tags=["AI Investigation"])
def explain_batch_findings(batch_id: str) -> dict:
    """
    Retrieves a stored batch, validates it deterministically, and asks
    the local LLM to explain the findings with recommended actions.
    """
    batch = batch_service.get_batch_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found."
        )
    # 1. Ensure batch has deterministic validation results
    report = batch.get("last_audit_report")
    if not report:
        report = batch_service.validate_existing_batch(batch_id)
    # 2. Call local LLM service
    llm_result = explain_qc_findings_with_llm(
        batch_id=batch_id,
        compound_name=batch.get("compound_name", "Unknown"),
        audit_report=report
    )
    if not llm_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=llm_result["error"]
        )
    return {
        "batch_id": batch_id,
        "compound": batch.get("compound_name"),
        "audit_report": report,
        "ai_explanation": llm_result["analysis"]
    }