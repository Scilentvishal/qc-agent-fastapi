sample_batch: str = "PARACETAMOL-BATCH-88"
ph_level: float = 7.2
min_ph: float = 5.8
max_ph: float = 6.8
ph_passed: bool = min_ph <= ph_level <= max_ph

print(f"Batch {sample_batch} is {'Passed' if ph_passed else 'Failed'}")