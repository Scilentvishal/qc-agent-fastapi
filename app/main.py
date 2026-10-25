# app/main.py
from app.services.batch_service import ACTIVE_SOP_SPECIFICATIONS
from app.core.validator import validate_qc_batch
from app.schemas.schemas import BatchValidationRequest
from fastapi import FastAPI
from app.api.batches import router as batch_router

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Pharma QC Intelligence Agent API",
    description="Educational pharmaceutical quality-control assistant with deterministic rule validation and agentic workflows.",
    version="0.2.0"
)

# 2. Include Modular Routers
app.include_router(batch_router)


# 3. System & Health Endpoints
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
        "agent_engine": "ready"
    }


# 4. Direct ad-hoc validation endpoint
@app.post("/qc/validate-batch", tags=["QC Validation"])
def validate_ad_hoc_batch(payload: BatchValidationRequest) -> dict:
    """Validates an ad-hoc batch payload directly without persisting it."""
    report = validate_qc_batch(payload.model_dump(), ACTIVE_SOP_SPECIFICATIONS)
    return {
        "success": True,
        "compound": payload.compound_name,
        "report": report
    }