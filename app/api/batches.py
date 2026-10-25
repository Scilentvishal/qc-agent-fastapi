# app/api/batches.py
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