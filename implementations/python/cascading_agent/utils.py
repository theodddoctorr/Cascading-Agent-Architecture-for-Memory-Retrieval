"""
Utility functions for the cascading agent architecture.
"""

import numpy as np
from typing import List, Union


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score between -1 and 1
    """
    if len(vec1.shape) == 1:
        vec1 = vec1.reshape(1, -1)
    if len(vec2.shape) == 1:
        vec2 = vec2.reshape(1, -1)

    dot_product = np.dot(vec1, vec2.T)
    norm1 = np.linalg.norm(vec1, axis=1, keepdims=True)
    norm2 = np.linalg.norm(vec2, axis=1, keepdims=True)

    similarity = dot_product / (norm1 * norm2.T + 1e-8)
    return float(similarity[0, 0])


def normalize_vector(vec: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to unit length.

    Args:
        vec: Input vector

    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def batch_cosine_similarity(
    query: np.ndarray,
    vectors: np.ndarray
) -> np.ndarray:
    """
    Calculate cosine similarity between a query and multiple vectors.

    Args:
        query: Query vector
        vectors: Array of vectors to compare against

    Returns:
        Array of similarity scores
    """
    if len(query.shape) == 1:
        query = query.reshape(1, -1)

    dot_products = np.dot(vectors, query.T)
    query_norm = np.linalg.norm(query)
    vector_norms = np.linalg.norm(vectors, axis=1, keepdims=True)

    similarities = dot_products / (vector_norms * query_norm + 1e-8)
    return similarities.flatten()


def exponential_decay(
    base_value: float,
    time_elapsed: float,
    half_life: float
) -> float:
    """
    Calculate exponential decay for memory access patterns.

    Args:
        base_value: Initial value
        time_elapsed: Time since last access
        half_life: Half-life for decay

    Returns:
        Decayed value
    """
    return base_value * (0.5 ** (time_elapsed / half_life))


def rank_results(
    scores: List[float],
    metadata: List[dict],
    top_k: int = 10
) -> List[tuple]:
    """
    Rank results by score and return top-k.

    Args:
        scores: List of similarity scores
        metadata: List of metadata dictionaries
        top_k: Number of top results to return

    Returns:
        List of (score, metadata) tuples
    """
    ranked = sorted(
        zip(scores, metadata),
        key=lambda x: x[0],
        reverse=True
    )
    return ranked[:top_k]
