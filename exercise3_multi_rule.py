SOP_LIMITS: dict[str, dict] = {
"dissolution": {
    "min": 80.0,
    "max": 100.0
},
"Impurities":{
    "min":0.0,
    "max": 0.5
}
}

sample_tests: list[dict]= [
    {
        "test_name": "dissolution",
        "measured_value": 85.5
    },
    {
        "test_name": "Impurities",
        "measured_value": 0.3
    },
    {
        "test_name": "Heavy Metals",
        "measured_value": 12.0
    }
]


deviations: list[str] = []

for test in sample_tests:
    name: str= test.get("test_name", "")
    value: float= test.get("measured_value", 0.0)
    
    if name not in SOP_LIMITS:
        deviations.append(f"No SOP Rule Found For {name}")
        continue
    
    rule: dict = SOP_LIMITS[name]
    min_value: float = rule.get("min")
    max_value: float = rule.get("max")

    if  min_value <= value <= max_value:
        print(f"[PASS] {name}")
    else:
        msg = f"[FAIL] {name}: {value} is OUT OF SPEC"
        print(msg)
        deviations.append(msg)

    
batch_passed: bool = len(deviations) == 0
print("\n=== Final Batch Result ===")
print(f"Overall Status: {'PASSED' if batch_passed else 'REJECTED'}")
print(f"Total Deviations: {len(deviations)}")
    
