# exercise2_sample_record.py

# 1. Structured injectable vial QC record
qc_sample: dict = {
    "lot_number": "LOT-INJ-501",
    "product": "Insulin Glargine",
    "release_status": "Pending",
    "parameters": {
        "endotoxin_units": 0.15,
        "particulate_count": 12
    }
}

# 2. Extract lot and product
lot: str = qc_sample["lot_number"]
product: str = qc_sample["product"]

# 3. Safe lookup for missing key with default
stability: str = qc_sample.get("stability_study", "Not Applicable")

# 4. Nested dictionary access
endotoxin: float = qc_sample["parameters"]["endotoxin_units"]

# 5. Formatted output
print(f"Product: {product} (Lot: {lot})")
print(f"Stability Study: {stability}")
print(f"Endotoxin Level: {endotoxin} EU/mL")
