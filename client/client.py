from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import tenseal as ts
import base64
import requests
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BACKEND_URL = "http://127.0.0.1:8000/compute"

# -------------------------
# Encryption helpers
# -------------------------


def create_context():
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    context.generate_galois_keys()
    context.generate_relin_keys()
    context.global_scale = 2**40
    return context


def encrypt_values(context, values):
    encrypted = []
    for v in values:
        enc = ts.ckks_vector(context, [v])
        encrypted.append(base64.b64encode(enc.serialize()).decode())
    return encrypted


def decrypt_result(context, encrypted_result):
    raw = base64.b64decode(encrypted_result)
    vec = ts.ckks_vector_from(context, raw)
    return vec.decrypt()[0]

# -------------------------
# API models
# -------------------------


class AnalyzeRequest(BaseModel):
    values: List[float]
    operation: str  # "sum" or "average"


class AnalyzeResponse(BaseModel):
    result: float

# -------------------------
# API endpoint
# -------------------------


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    context = create_context()

    encrypted_vectors = encrypt_values(context, req.values)

    payload = {
        "context": base64.b64encode(
            context.serialize(save_secret_key=False)
        ).decode(),
        "encrypted_vectors": encrypted_vectors,
        "operation": req.operation,
    }

    response = requests.post(BACKEND_URL, json=payload)
    response.raise_for_status()

    encrypted_result = response.json()["encrypted_result"]
    result = decrypt_result(context, encrypted_result)

    return {"result": result}
