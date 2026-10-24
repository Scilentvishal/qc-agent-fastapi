# lesson3_qc_validator.py

# 1. Synthetic SOP specification limits: (min, max, unit)
SOP_LIMITS: dict[str, dict] = {
    "Assay": {"min": 98.0, "max": 102.0, "unit": "%"},
    "pH": {"min": 5.0, "max": 6.5, "unit": "pH"},
    "Water Content": {"min": 10.0, "max": 14.5, "unit": "%"},
}

# 2. Sample batch test results
sample_tests: list[dict] = [
    {"test_name": "Assay", "measured_value": 99.4},
    {"test_name": "pH", "measured_value": 4.8},            # Out of spec (low)
    {"test_name": "Water Content", "measured_value": 15.2}, # Out of spec (high)
]

# 3. Deterministic validation loop
deviations: list[str] = []

print("=== Running Deterministic QC Validation ===")

for test in sample_tests:
    name: str = test["test_name"]
    val: float = test["measured_value"]

    # Check if this test exists in our SOP rules
    if name not in SOP_LIMITS:
        deviations.append(f"No SOP rule defined for test: {name}")
        continue

    rule: dict = SOP_LIMITS[name]
    min_val: float = rule["min"]
    max_val: float = rule["max"]
    unit: str = rule["unit"]

    # Evaluate limits
    if min_val <= val <= max_val:
        print(f"[PASS] {name}: {val} {unit} (Spec: {min_val} - {max_val} {unit})")
    else:
        msg = f"[FAIL] {name}: {val} {unit} is OUT OF SPEC (Allowed: {min_val} - {max_val} {unit})"
        print(msg)
        deviations.append(msg)

# 4. Final disposition
batch_passed: bool = len(deviations) == 0
print("\n=== Final Batch Result ===")
print(f"Overall Status: {'PASSED' if batch_passed else 'REJECTED'}")
print(f"Total Deviations: {len(deviations)}")