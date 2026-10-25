# app/core/validator.py

def validate_measurement(test_name: str, value: float, limits: dict) -> dict:
    """Validates a single measurement against min/max limits."""
    min_val: float = limits["min"]
    max_val: float = limits["max"]
    unit: str = limits.get("unit", "")

    passed: bool = min_val <= value <= max_val
    msg = "Compliant" if passed else f"Out of specification: {value} {unit} not in [{min_val}, {max_val}]"

    return {
        "test_name": test_name,
        "value": value,
        "unit": unit,
        "passed": passed,
        "message": msg
    }


def validate_qc_batch(batch_data: dict, sop_specifications: dict) -> dict:
    """Validates all tests in a batch record against SOP specifications."""
    batch_id: str = batch_data.get("batch_id", "UNKNOWN")
    tests: list[dict] = batch_data.get("tests", [])

    deviations: list[str] = []
    audit_results: list[dict] = []

    for test in tests:
        name = test.get("test_name", "")
        val = test.get("measured_value", 0.0)

        if name not in sop_specifications:
            err = f"No SOP specification exists for '{name}'"
            deviations.append(err)
            audit_results.append({"test_name": name, "passed": False, "message": err})
            continue

        result = validate_measurement(name, val, sop_specifications[name])
        audit_results.append(result)

        if not result["passed"]:
            deviations.append(result["message"])

    is_approved: bool = len(deviations) == 0

    return {
        "batch_id": batch_id,
        "is_approved": is_approved,
        "total_tests": len(tests),
        "deviation_count": len(deviations),
        "deviations": deviations,
        "details": audit_results
    }