"""
use_embeddings.py

Loads the Universal Sentence Encoder (USE) from TensorFlow Hub and
exposes functions to encode text into 512-dimensional embedding vectors.

Responsibilities:
- Load the USE model once and cache it globally
- Encode single strings
- Encode batches of strings
- Return NumPy arrays

This module is ONLY responsible for: text → embedding vector.
Similarity scoring lives in a separate layer.
"""

import logging
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model URL and global cache
# ---------------------------------------------------------------------------

_USE_MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"

_model: hub.KerasLayer | None = None


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model() -> hub.KerasLayer:
    """
    Load the USE model and cache it globally.

    Subsequent calls return the cached instance without reloading.
    Downloads the model on first call (~1 GB, cached locally by TF Hub).
    """
    global _model
    if _model is None:
        logger.info("Loading Universal Sentence Encoder from TF Hub...")
        _model = hub.load(_USE_MODEL_URL)
        logger.info("USE model loaded successfully.")
    return _model


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def encode_text(text: str) -> np.ndarray:
    """
    Encode a single string into a 512-dimensional embedding vector.

    Args:
        text: Input string to encode.

    Returns:
        NumPy array of shape (512,).
        Returns a zero vector if input is empty or whitespace-only.
    """
    if not text or not text.strip():
        return np.zeros(512, dtype=np.float32)

    model = load_model()
    embeddings = model([text])
    return np.array(embeddings[0], dtype=np.float32)


def encode_batch(texts: list[str]) -> np.ndarray:
    """
    Encode a list of strings into a matrix of 512-dimensional embeddings.

    Args:
        texts: List of input strings.

    Returns:
        NumPy array of shape (len(texts), 512).
        Empty-string entries are replaced with zero vectors.
        Returns empty array of shape (0, 512) if the list is empty.
    """
    if not texts:
        return np.zeros((0, 512), dtype=np.float32)

    # Sanitize: replace empty/whitespace entries with a single space
    # so USE receives valid input; zero out their results afterward.
    empty_mask = [not t or not t.strip() for t in texts]
    sanitized = [" " if empty else t for empty, t in zip(empty_mask, texts)]

    model = load_model()
    embeddings = np.array(model(sanitized), dtype=np.float32)

    # Zero out embeddings for originally empty inputs
    for i, was_empty in enumerate(empty_mask):
        if was_empty:
            embeddings[i] = 0.0

    return embeddings