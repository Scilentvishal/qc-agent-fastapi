# tests/test_batches.py
from fastapi.testclient import TestClient
from app.main import app

# Initialize in-memory test client
client = TestClient(app)


def test_health_check():
    """Verify system health endpoint responds with 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agent_engine"] == "ready"


def test_create_batch_success():
    """Verify creating a new valid batch returns 201 Created."""
    payload = {
        "batch_id": "BATCH-TEST-2026-A1",
        "compound_name": "Paracetamol 500mg",
        "tests": [
            {"test_name": "Assay", "measured_value": 99.8},
            {"test_name": "pH", "measured_value": 6.2}
        ]
    }
    response = client.post("/batches", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["batch_id"] == "BATCH-TEST-2026-A1"
    assert data["record"]["validation_status"] == "PENDING_VALIDATION"


def test_create_duplicate_batch_fails():
    """Verify creating a batch with an existing ID returns 400 Bad Request."""
    payload = {
        "batch_id": "BATCH-TEST-2026-A1",  # Same ID as previous test
        "compound_name": "Paracetamol 500mg",
        "tests": [{"test_name": "Assay", "measured_value": 100.0}]
    }
    response = client.post("/batches", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_existing_batch():
    """Verify retrieving an existing batch returns 200 OK with correct data."""
    response = client.get("/batches/BATCH-TEST-2026-A1")
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "BATCH-TEST-2026-A1"
    assert len(data["tests"]) == 2


def test_get_nonexistent_batch_returns_404():
    """Verify fetching an unknown batch ID returns 404 Not Found."""
    response = client.get("/batches/DOES-NOT-EXIST-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Batch 'DOES-NOT-EXIST-999' not found."


def test_validate_stored_batch():
    """Verify running QC validation evaluates tests and marks batch compliant."""
    response = client.post("/batches/BATCH-TEST-2026-A1/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "BATCH-TEST-2026-A1"
    # Both Assay 99.8 and pH 6.2 are within spec
    assert data["is_approved"] is True
    assert data["audit_report"]["deviation_count"] == 0


def test_invalid_payload_triggers_422():
    """Verify sending corrupted data types is caught by Pydantic (422 Unprocessable Entity)."""
    corrupted_payload = {
        "batch_id": "BATCH-BAD-01",
        "compound_name": "Ibuprofen",
        "tests": [
            {"test_name": "pH", "measured_value": "NOT_A_NUMBER"}  # Invalid float
        ]
    }
    response = client.post("/batches", json=corrupted_payload)
    assert response.status_code == 422