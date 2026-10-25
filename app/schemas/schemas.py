# app/schemas.py
from pydantic import BaseModel, Field


class TestMeasurement(BaseModel):
    """Schema for an individual test reading in a batch."""
    test_name: str = Field(..., description="Name of the physical or chemical test", example="Assay")
    measured_value: float = Field(..., description="Measured laboratory numerical result", example=99.5)


class BatchValidationRequest(BaseModel):
    """Incoming request payload to validate a batch record."""
    batch_id: str = Field(..., description="Unique lot or batch identifier", example="BATCH-2026-ASP-01")
    compound_name: str = Field(..., description="Active pharmaceutical ingredient name", example="Aspirin 500mg")
    tests: list[TestMeasurement] = Field(..., description="List of recorded laboratory test measurements") 