"""
similarity.py

Computes semantic similarity between embedding vectors using cosine similarity.

Responsibilities:
- Compare two embedding vectors
- Compare two raw text strings (via USE)
- Batch pairwise comparison

Returns scores in [0.0, 1.0].
Zero vectors are handled safely — similarity returns 0.0.
"""

import numpy as np

from backend.app.ml.embeddings.use_embeddings import encode_text


# ---------------------------------------------------------------------------
# Core similarity
# ---------------------------------------------------------------------------

def cosine_similarity(
    embedding_a: np.ndarray,
    embedding_b: np.ndarray,
) -> float:
    """
    Compute cosine similarity between two 1-D embedding vectors.

    Args:
        embedding_a: NumPy array of shape (D,).
        embedding_b: NumPy array of shape (D,).

    Returns:
        Float in [0.0, 1.0].
        Returns 0.0 if either vector is a zero vector.
    """
    norm_a = np.linalg.norm(embedding_a)
    norm_b = np.linalg.norm(embedding_b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    raw = float(np.dot(embedding_a, embedding_b) / (norm_a * norm_b))

    # Clamp to [0, 1]: negative cosine similarity has no useful meaning
    # in this context (semantically unrelated answers, not opposites).
    return float(np.clip(raw, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Text-level convenience
# ---------------------------------------------------------------------------

def similarity_from_texts(text_a: str, text_b: str) -> float:
    """
    Encode two strings and return their cosine similarity.

    Args:
        text_a: First text (e.g. ideal answer).
        text_b: Second text (e.g. candidate answer).

    Returns:
        Float in [0.0, 1.0].
    """
    embedding_a = encode_text(text_a)
    embedding_b = encode_text(text_b)
    return cosine_similarity(embedding_a, embedding_b)


# ---------------------------------------------------------------------------
# Batch comparison
# ---------------------------------------------------------------------------

def batch_similarity(
    embeddings_a: np.ndarray,
    embeddings_b: np.ndarray,
) -> np.ndarray:
    """
    Compute element-wise cosine similarity for two (N, D) embedding matrices.

    Each row i of embeddings_a is compared against row i of embeddings_b.

    Args:
        embeddings_a: NumPy array of shape (N, D).
        embeddings_b: NumPy array of shape (N, D).

    Returns:
        NumPy array of shape (N,) with similarity scores in [0.0, 1.0].
        Rows where either vector is zero return 0.0.
    """
    if embeddings_a.shape != embeddings_b.shape:
        raise ValueError(
            f"Shape mismatch: {embeddings_a.shape} vs {embeddings_b.shape}"
        )

    if embeddings_a.ndim != 2:
        raise ValueError(
            f"Expected 2-D arrays, got shape {embeddings_a.shape}"
        )

    norms_a = np.linalg.norm(embeddings_a, axis=1, keepdims=True)  # (N, 1)
    norms_b = np.linalg.norm(embeddings_b, axis=1, keepdims=True)  # (N, 1)

    # Replace zero norms with 1.0 to avoid divide-by-zero;
    # dot products for those rows will naturally be 0.0.
    norms_a = np.where(norms_a == 0.0, 1.0, norms_a)
    norms_b = np.where(norms_b == 0.0, 1.0, norms_b)

    normalized_a = embeddings_a / norms_a
    normalized_b = embeddings_b / norms_b

    # Row-wise dot product
    dot_products = np.sum(normalized_a * normalized_b, axis=1)  # (N,)

    return np.clip(dot_products, 0.0, 1.0).astype(np.float32)
