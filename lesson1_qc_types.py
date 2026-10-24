# lesson1_qc_types.py

# 1. Defining QC batch parameters with explicit type hints
sample_id: str = "SOP-ASSAY-001"
active_ingredient_percentage: float = 99.4
target_minimum: float = 98.0
target_maximum: float = 102.0

# 2. Deterministic rule check
is_compliant: bool = target_minimum <= active_ingredient_percentage <= target_maximum

# 3. Handling optional/nullable values
deviation_notes: str | None = None

# 4. Displaying the QC status
print("=== Pharmaceutical QC Sample Report ===")
print(f"Sample ID: {sample_id}")
print(f"Active Ingredient: {active_ingredient_percentage}%")
print(f"Specification: {target_minimum}% - {target_maximum}%")
print(f"Is Compliant: {is_compliant}")
print(f"Deviation Notes: {deviation_notes}")