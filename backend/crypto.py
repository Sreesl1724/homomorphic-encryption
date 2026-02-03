import tenseal as ts

def load_context(context_bytes: bytes):
    """
    Load TenSEAL context from serialized bytes.
    Backend gets ONLY public context.
    """
    return ts.context_from(context_bytes)


def deserialize_vector(context, data: bytes):
    """
    Rebuild encrypted CKKS vector using provided context.
    """
    return ts.ckks_vector_from(context, data)


def compute_sum(vectors):
    """
    Perform homomorphic sum on encrypted vectors.
    """
    result = vectors[0]
    for v in vectors[1:]:
        result += v
    return result


def compute_average(vectors):
    """
    Perform homomorphic average on encrypted vectors.
    """
    total = compute_sum(vectors)
    avg = total * (1 / len(vectors))
    return avg

