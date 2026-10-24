# lesson2_batch_records.py

# 1. Defining a structured QC batch record using a nested dictionary
batch_record: dict = {
    "batch_id": "AMX-2026-B102",
    "compound": "Amoxicillin Trihydrate",
    "dosage_form": "Capsule",
    "tests": [
        {"test_name": "Assay", "measured_value": 99.1, "unit": "%"},
        {"test_name": "pH", "measured_value": 5.2, "unit": "pH"},
        {"test_name": "Water Content", "measured_value": 13.8, "unit": "%"}
    ]
}

# 2. Extracting basic batch metadata safely
batch_id: str = batch_record.get("batch_id", "UNKNOWN")
inspector: str | None = batch_record.get("inspector")  # Missing key returns None safely

print(f"Inspecting Batch: {batch_id}")
print(f"Assigned Inspector: {inspector if inspector else 'None Assigned'}")

# 3. Accessing elements inside the list
test_list: list[dict] = batch_record["tests"]
print(f"Total QC tests performed: {len(test_list)}")

# 4. Accessing the first test
first_test: dict = test_list[0]
print(f"First Test: {first_test['test_name']} -> {first_test['measured_value']} {first_test['unit']}")