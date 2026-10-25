# app/main.py
from fastapi import HTTPException
from fastapi import status
from app.core.validator import validate_qc_batch
from app.schemas.schemas import BatchValidationRequest
from fastapi import FastAPI

# 1. Initialize application
app = FastAPI(
    title="Pharma QC Intelligence Agent API",
    description="Educational pharmaceutical quality-control assistant with deterministic rule validation and agentic workflows.",
    version="0.1.0"
)

# 2. Synthetic in-memory database
BATCH_DATABASE: dict[str, dict] = {}

# 2. Hardcoded synthetic SOP specifications (we will load from disk/DB in Phase 3)
ACTIVE_SOP_SPECIFICATIONS: dict[str, dict] = {
    "Assay": {"min": 98.0, "max": 102.0, "unit": "%"},
    "pH": {"min": 5.8, "max": 6.8, "unit": "pH"},
    "Dissolution": {"min": 80.0, "max": 100.0, "unit": "%"}
}


@app.get("/", tags=["System"])
def root() -> dict:
    return {
        "service": "Pharma QC Intelligence Agent",
        "status": "online",
        "documentation": "/docs"
    }


@app.get("/health", tags=["System"])
def health_check() -> dict:
    return {
        "status": "healthy",
        "database": "in-memory (initial phase)",
        "agent_engine": "ready"
    }


# --- Batch Record CRUD Endpoints ---
@app.post("/batches", status_code=status.HTTP_201_CREATED, tags=["Batches"])
def create_batch(payload: BatchValidationRequest) -> dict:
    """
    Submits and stores a new sample batch record in memory.
    Returns 201 Created.
    """
    batch_id = payload.batch_id
    if batch_id in BATCH_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch with ID '{batch_id}' already exists."
        )
    # Store in memory
    stored_record = payload.model_dump()
    stored_record["validation_status"] = "PENDING_VALIDATION"
    BATCH_DATABASE[batch_id] = stored_record
    return {
        "message": "Batch record created successfully",
        "batch_id": batch_id,
        "record": stored_record
    }
    
@app.get("/batches", tags=["Batches"])
def list_batches(limit: int = 10, skip: int = 0) -> dict:
    """
    Lists stored batch records with query parameters for pagination.
    Example: /batches?limit=5&skip=0
    """
    all_batches = list(BATCH_DATABASE.values())
    paginated = all_batches[skip : skip + limit]
    return {
        "total_count": len(all_batches),
        "limit": limit,
        "skip": skip,
        "batches": paginated
    }
@app.get("/batches/{batch_id}", tags=["Batches"])
def get_batch(batch_id: str) -> dict:
    """
    Retrieves a single batch record by its unique batch ID.
    Raises 404 if not found.
    """
    if batch_id not in BATCH_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found."
        )
    return BATCH_DATABASE[batch_id]

    
# --- QC Validation Endpoint ---
@app.post("/batches/{batch_id}/validate", tags=["QC Validation"])
def validate_stored_batch(batch_id: str) -> dict:
    """
    Runs deterministic QC validation against a stored batch record.
    Updates the batch's validation status in memory.
    """
    if batch_id not in BATCH_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch '{batch_id}' not found."
        )
    batch_record = BATCH_DATABASE[batch_id]
    # Run deterministic engine
    report = validate_qc_batch(
        batch_data=batch_record,
        sop_specifications=ACTIVE_SOP_SPECIFICATIONS
    )
    # Update state in memory
    batch_record["validation_status"] = "APPROVED" if report["is_approved"] else "FLAGGED_FOR_REVIEW"
    batch_record["last_audit_report"] = report
    return {
        "batch_id": batch_id,
        "is_approved": report["is_approved"],
        "validation_status": batch_record["validation_status"],
        "audit_report": report
    }