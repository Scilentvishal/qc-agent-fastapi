# run_check.

from app.core.validator import validate_qc_batch

if __name__ == "__main__":
    synthetic_sop = {
        "Assay": {"min": 98.0, "max": 102.0, "unit": "%"},
        "pH": {"min": 5.8, "max": 6.8, "unit": "pH"}
    }

    synthetic_batch = {
        "batch_id": "BATCH-PROD-2026-001",
        "tests": [
            {"test_name": "Assay", "measured_value": 99.5},
            {"test_name": "pH", "measured_value": 7.4}  # Should fail
        ]
    }

    report = validate_qc_batch(synthetic_batch, synthetic_sop)

    print("=== Modular QC Engine Test ===")
    print(f"Batch ID: {report['batch_id']}")
    print(f"Approved: {report['is_approved']}")
    print(f"Deviations: {report['deviations']}")