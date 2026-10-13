from __future__ import annotations

import hashlib
import math
from typing import Any


VOYAGE_MODEL_ID = "voyage-3-lite"
VOYAGE_VECTOR_DIMENSION = 512


class VectorDimensionMismatchError(ValueError):
    """Raised when an embedding vector does not match the configured Voyage 512 dimension."""
    pass


def validate_vector_dimension(
    vector: list[float] | tuple[float, ...],
    expected_dim: int = VOYAGE_VECTOR_DIMENSION,
) -> None:
    if len(vector) != expected_dim:
        raise VectorDimensionMismatchError(
            f"Embedding vector dimension {len(vector)} does not match expected Voyage dimension {expected_dim}."
        )


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    validate_vector_dimension(v1)
    validate_vector_dimension(v2)
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def generate_mock_embedding(text: str, dimension: int = VOYAGE_VECTOR_DIMENSION) -> list[float]:
    """Deterministic, zero-quota unit embedding representation for testing RAG search."""
    cleaned = text.strip().encode("utf-8")
    seed_hash = hashlib.sha256(cleaned).digest()
    values: list[float] = []
    for i in range(dimension):
        byte_val = seed_hash[i % len(seed_hash)]
        # Normalize into [-1.0, 1.0] range
        val = (byte_val / 127.5) - 1.0 + (i * 0.001)
        values.append(val)
    # Unit normalize
    norm = math.sqrt(sum(x * x for x in values)) or 1.0
    return [x / norm for x in values]


def get_rag_vector_schema() -> dict[str, Any]:
    return {
        "provider": "voyage",
        "model": VOYAGE_MODEL_ID,
        "dimension": VOYAGE_VECTOR_DIMENSION,
        "pgvector_column": f"vector({VOYAGE_VECTOR_DIMENSION})",
        "distance_metric": "cosine",
        "status": "aligned_pre_production",
    }
