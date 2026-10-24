# exercise4_reusable_validator.py

def calculate_batch_yield(theoretical_yield: float, actual_yield: float) -> dict:
    """
    Calculates the batch yield percentage and checks if it falls
    within standard pharmaceutical acceptable limits (95.0% to 102.0%).
    """
    # Defensive check against division by zero
    if theoretical_yield <= 0:
        return {
            "theoretical": theoretical_yield,
            "actual": actual_yield,
            "percentage": 0.0,
            "is_acceptable": False,
            "discrepancy_note": "Invalid theoretical yield: must be greater than zero."
        }

    # 1. Calculate yield percentage
    yield_percentage: float = (actual_yield / theoretical_yield) * 100.0
    rounded_pct: float = round(yield_percentage, 2)

    # 2. Synthetic QC acceptance limits
    min_yield: float = 95.0
    max_yield: float = 102.0

    is_acceptable: bool = min_yield <= rounded_pct <= max_yield

    # 3. Discrepancy note (remains None if acceptable)
    discrepancy_note: str | None = None
    if not is_acceptable:
        if rounded_pct < min_yield:
            discrepancy_note = f"Yield below specification: {rounded_pct}% (Minimum required: {min_yield}%)"
        else:
            discrepancy_note = f"Yield above specification: {rounded_pct}% (Maximum allowed: {max_yield}%)"

    return {
        "theoretical": theoretical_yield,
        "actual": actual_yield,
        "percentage": rounded_pct,
        "is_acceptable": is_acceptable,
        "discrepancy_note": discrepancy_note
    }


# Standalone execution test block
if __name__ == "__main__":
    print("=== Testing Batch Yield Calculation ===")

    # Test Case A: Compliant batch (492g out of 500g = 98.4%)
    case_a = calculate_batch_yield(theoretical_yield=500.0, actual_yield=492.0)
    print("\nCase A (Expected PASS):")
    print(f"Percentage: {case_a['percentage']}%")
    print(f"Acceptable: {case_a['is_acceptable']}")
    print(f"Note: {case_a['discrepancy_note']}")

    # Test Case B: Non-compliant batch (460g out of 500g = 92.0%)
    case_b = calculate_batch_yield(theoretical_yield=500.0, actual_yield=460.0)
    print("\nCase B (Expected FAIL):")
    print(f"Percentage: {case_b['percentage']}%")
    print(f"Acceptable: {case_b['is_acceptable']}")
    print(f"Note: {case_b['discrepancy_note']}")