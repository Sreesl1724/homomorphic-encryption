import tenseal as ts
import requests
import base64
import json

# -------------------------------
# Create TenSEAL context (CLIENT)
# -------------------------------
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60],
)

context.generate_galois_keys()
context.global_scale = 2**40

# -------------------------------
# Serialize PUBLIC context only
# -------------------------------
context_bytes = context.serialize(
    save_secret_key=False,
    save_galois_keys=True,
    save_relin_keys=True
)

context_b64 = base64.b64encode(context_bytes).decode("utf-8")

# -------------------------------
# Encrypt data
# -------------------------------
values = [45, 130, 210]
encrypted_vectors = []

for v in values:
    vec = ts.ckks_vector(context, [float(v)])
    encrypted_vectors.append(
        base64.b64encode(vec.serialize()).decode("utf-8")
    )

# -------------------------------
# Build payload
# -------------------------------
payload = {
    "context": context_b64,
    "encrypted_vectors": encrypted_vectors,
    "operation": "average"   # 🔁 change to "sum" if needed
}

# -------------------------------
# Send request to backend
# -------------------------------
response = requests.post(
    "http://127.0.0.1:8000/compute",
    data=json.dumps(payload),
    headers={"Content-Type": "application/json"},
    timeout=5
)

# -------------------------------
# Handle response
# -------------------------------
data = response.json()

encrypted_result_bytes = base64.b64decode(data["encrypted_result"])
encrypted_result_vec = ts.ckks_vector_from(context, encrypted_result_bytes)
result = encrypted_result_vec.decrypt()[0]

print("Plain values:", values)
print("Decrypted result from backend:", result)
