from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import base64

from crypto import (
    load_context,
    deserialize_vector,
    compute_sum,
    compute_average
)

app = FastAPI()


class ComputeRequest(BaseModel):
    context: str                 # base64 encoded public context
    encrypted_vectors: List[str]  # base64 encoded ciphertexts
    operation: str               # "sum" or "average"


class ComputeResponse(BaseModel):
    encrypted_result: str


class PopulationRequest(BaseModel):
    public_context: str              # hex encoded public context
    encrypted_values: List[str]      # hex encoded CKKS vectors


class PopulationResponse(BaseModel):
    encrypted_average: str           # hex encoded encrypted result


@app.post("/compute", response_model=ComputeResponse)
def compute(req: ComputeRequest):
    context_bytes = base64.b64decode(req.context)
    context = load_context(context_bytes)

    vectors = []
    for vec_str in req.encrypted_vectors:
        raw_bytes = base64.b64decode(vec_str)
        vec = deserialize_vector(context, raw_bytes)
        vectors.append(vec)

    if req.operation == "sum":
        encrypted_result = compute_sum(vectors)
    elif req.operation == "average":
        encrypted_result = compute_average(vectors)
    else:
        raise ValueError("Unsupported operation")

    return {
        "encrypted_result": base64.b64encode(
            encrypted_result.serialize()
        ).decode("utf-8")
    }


@app.post("/population/average", response_model=PopulationResponse)
def encrypted_population_average(req: PopulationRequest):

    # Public context only — backend cannot decrypt
    context_bytes = bytes.fromhex(req.public_context)
    context = load_context(context_bytes)

    vectors = []
    for v_hex in req.encrypted_values:
        v_bytes = bytes.fromhex(v_hex)
        vec = deserialize_vector(context, v_bytes)
        vectors.append(vec)

    encrypted_avg = compute_average(vectors)

    return {
        "encrypted_average": encrypted_avg.serialize().hex()
    }
