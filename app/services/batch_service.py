# app/services/batch_service.py
from app.core.validator import validate_qc_batch

# In-memory storage dedicated to batch service
BATCH_DATABASE: dict[str, dict] = {}

# Active SOP specification rules
ACTIVE_SOP_SPECIFICATIONS: dict[str, dict] = {
    "Assay": {"min": 98.0, "max": 102.0, "unit": "%"},
    "pH": {"min": 5.8, "max": 6.8, "unit": "pH"},
    "Dissolution": {"min": 80.0, "max": 100.0, "unit": "%"}
}


def create_new_batch(batch_data: dict) -> dict | None:
    """Stores a new batch record. Returns None if already exists."""
    batch_id = batch_data["batch_id"]
    if batch_id in BATCH_DATABASE:
        return None

    record = dict(batch_data)
    record["validation_status"] = "PENDING_VALIDATION"
    BATCH_DATABASE[batch_id] = record
    return record


def get_all_batches(skip: int = 0, limit: int = 10) -> list[dict]:
    """Returns paginated batch records."""
    all_records = list(BATCH_DATABASE.values())
    return all_records[skip : skip + limit]


def get_batch_by_id(batch_id: str) -> dict | None:
    """Returns batch record or None if not found."""
    return BATCH_DATABASE.get(batch_id)


def validate_existing_batch(batch_id: str) -> dict | None:
    """Validates an existing batch against SOP specifications."""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return None

    report = validate_qc_batch(batch, ACTIVE_SOP_SPECIFICATIONS)
    batch["validation_status"] = "APPROVED" if report["is_approved"] else "FLAGGED_FOR_REVIEW"
    batch["last_audit_report"] = report
    return report