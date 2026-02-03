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
    encrypted_vectors: List[str] # base64 encoded ciphertexts
    operation: str               # "sum" or "average"


class ComputeResponse(BaseModel):
    encrypted_result: str


@app.post("/compute", response_model=ComputeResponse)
def compute(req: ComputeRequest):
    # Decode and load context (public only)
    context_bytes = base64.b64decode(req.context)
    context = load_context(context_bytes)

    # Deserialize encrypted vectors
    vectors = []
    for vec_str in req.encrypted_vectors:
        raw_bytes = base64.b64decode(vec_str)
        vec = deserialize_vector(context, raw_bytes)
        vectors.append(vec)

    # Route operation
    if req.operation == "sum":
        encrypted_result = compute_sum(vectors)
    elif req.operation == "average":
        encrypted_result = compute_average(vectors)
    else:
        raise ValueError("Unsupported operation")

    # Return encrypted result
    return {
        "encrypted_result": base64.b64encode(
            encrypted_result.serialize()
        ).decode("utf-8")
    }
