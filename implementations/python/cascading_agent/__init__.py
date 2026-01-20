"""
Cascading Agent Architecture for Memory Retrieval

A reference implementation of the cascading agent architecture that provides
efficient multi-tier memory retrieval with automatic promotion and optimization.

Author: Jason Faulkner
License: Apache-2.0
"""

from .memory_tier import MemoryTier, TierConfig
from .retrieval import CascadingRetrieval, RetrievalStrategy
from .agent import CascadingAgent, AgentConfig
from .utils import cosine_similarity, normalize_vector
from .production import (
    ProductionAgent,
    create_production_agent,
    get_default_embedding_function
)

__version__ = "1.0.0"
__all__ = [
    "MemoryTier",
    "TierConfig",
    "CascadingRetrieval",
    "RetrievalStrategy",
    "CascadingAgent",
    "AgentConfig",
    "cosine_similarity",
    "normalize_vector",
    "ProductionAgent",
    "create_production_agent",
    "get_default_embedding_function",
]
