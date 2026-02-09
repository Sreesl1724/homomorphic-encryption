import json
import tenseal as ts

DATA_FILE = "data/kaggle/processed_patients.json"
OUTPUT_FILE = "data/kaggle/encrypted_glucose.json"

# -----------------------------
# 1. Load patient data
# -----------------------------
with open(DATA_FILE) as f:
    patients = json.load(f)

print(f"Loaded {len(patients)} patient records")

# -----------------------------
# 2. Create TenSEAL context (CKKS)
# -----------------------------
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60],
)
context.generate_galois_keys()
context.global_scale = 2 ** 40

# IMPORTANT: backend will only receive PUBLIC context
public_context = context.serialize(save_secret_key=False)

# -----------------------------
# 3. Encrypt glucose values (batch)
# -----------------------------
encrypted_vectors = []

for patient in patients:
    glucose_value = float(patient["glucose"])
    enc = ts.ckks_vector(context, [glucose_value])
    encrypted_vectors.append(enc.serialize())

print(f"Encrypted {len(encrypted_vectors)} glucose values")

# -----------------------------
# 4. Save encrypted batch + public context
# -----------------------------
output = {
    "public_context": public_context.hex(),
    "encrypted_glucose": [v.hex() for v in encrypted_vectors]
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(output, f)

print(f"Encrypted batch written to {OUTPUT_FILE}")
