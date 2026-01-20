"""
Production-ready enhancements for the Cascading Agent Architecture.

This module provides hardened versions of the core classes with:
- Better default embeddings
- Thread safety
- Memory limits and monitoring
- Error handling
- Logging
"""

import threading
import logging
from typing import Optional, Callable, List, Dict, Any
import numpy as np

from .agent import CascadingAgent, AgentConfig
from .memory_tier import TierConfig
from .retrieval import RetrievalStrategy


# Set up logging
logger = logging.getLogger(__name__)


class ProductionAgent(CascadingAgent):
    """
    Production-hardened version of CascadingAgent with:
    - Thread safety
    - Memory limits
    - Better error handling
    - Logging
    """

    def __init__(
        self,
        config: AgentConfig,
        max_items: int = 10000,
        enable_thread_safety: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize production agent.

        Args:
            config: Agent configuration
            max_items: Maximum total items across all tiers
            enable_thread_safety: Enable thread-safe operations
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        super().__init__(config)

        self.max_items = max_items
        self.enable_thread_safety = enable_thread_safety

        if enable_thread_safety:
            self._lock = threading.RLock()  # Reentrant lock
        else:
            self._lock = None

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger.info(f"ProductionAgent initialized with max_items={max_items}")

    def _check_capacity(self) -> bool:
        """Check if at capacity."""
        stats = self.get_stats()
        current_items = stats['total_items']

        if current_items >= self.max_items:
            logger.warning(
                f"At capacity: {current_items}/{self.max_items} items"
            )
            return False

        if current_items > self.max_items * 0.9:
            logger.warning(
                f"Approaching capacity: {current_items}/{self.max_items} items "
                f"({current_items/self.max_items:.1%})"
            )

        return True

    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[np.ndarray] = None,
        item_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add content with capacity checking.

        Args:
            content: Text content
            metadata: Optional metadata
            embedding: Pre-computed embedding
            item_id: Custom ID

        Returns:
            Item ID if added, None if at capacity
        """
        if self._lock:
            with self._lock:
                return self._add_impl(content, metadata, embedding, item_id)
        else:
            return self._add_impl(content, metadata, embedding, item_id)

    def _add_impl(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]],
        embedding: Optional[np.ndarray],
        item_id: Optional[str]
    ) -> Optional[str]:
        """Internal add implementation."""
        # Check capacity
        if not self._check_capacity():
            logger.error("Cannot add item: at capacity")
            return None

        # Validate input
        if not content or not content.strip():
            logger.error("Cannot add empty content")
            return None

        try:
            # Validate embedding if provided
            if embedding is not None:
                if not isinstance(embedding, np.ndarray):
                    logger.error("Embedding must be numpy array")
                    return None

                if np.any(np.isnan(embedding)) or np.any(np.isinf(embedding)):
                    logger.error("Embedding contains NaN or inf values")
                    return None

                # Normalize if needed
                norm = np.linalg.norm(embedding)
                if norm < 1e-10:
                    logger.warning("Near-zero embedding norm, normalizing")
                    embedding = embedding / (norm + 1e-10)

            result = super().add(content, metadata, embedding, item_id)
            logger.debug(f"Added item: {item_id or result}")
            return result

        except Exception as e:
            logger.error(f"Error adding item: {e}", exc_info=True)
            return None

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        max_tiers: Optional[int] = None,
        return_embeddings: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Thread-safe query with error handling.

        Args:
            query: Query text
            top_k: Number of results
            threshold: Similarity threshold
            max_tiers: Max tiers to search
            return_embeddings: Include embeddings

        Returns:
            List of results
        """
        if self._lock:
            with self._lock:
                return self._query_impl(
                    query, top_k, threshold, max_tiers, return_embeddings
                )
        else:
            return self._query_impl(
                query, top_k, threshold, max_tiers, return_embeddings
            )

    def _query_impl(
        self,
        query: str,
        top_k: Optional[int],
        threshold: Optional[float],
        max_tiers: Optional[int],
        return_embeddings: bool
    ) -> List[Dict[str, Any]]:
        """Internal query implementation."""
        if not query or not query.strip():
            logger.error("Cannot query with empty string")
            return []

        try:
            results = super().query(
                query, top_k, threshold, max_tiers, return_embeddings
            )
            logger.debug(f"Query returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error during query: {e}", exc_info=True)
            return []

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the agent.

        Returns:
            Health status dictionary
        """
        stats = self.get_stats()

        total_items = stats['total_items']
        capacity_pct = total_items / self.max_items if self.max_items > 0 else 0

        # Determine health status
        if capacity_pct >= 1.0:
            status = "CRITICAL"
        elif capacity_pct >= 0.9:
            status = "WARNING"
        elif capacity_pct >= 0.7:
            status = "HEALTHY"
        else:
            status = "OPTIMAL"

        # Check tier balance
        tier_stats = stats['tier_stats']
        tier_utilizations = [t['utilization'] for t in tier_stats]
        avg_utilization = sum(tier_utilizations) / len(tier_utilizations)

        return {
            "status": status,
            "total_items": total_items,
            "max_items": self.max_items,
            "capacity_used": capacity_pct,
            "avg_tier_utilization": avg_utilization,
            "total_queries": stats['query_stats']['total_queries'],
            "avg_latency_ms": stats['query_stats']['avg_latency_ms'],
            "promotions": stats['query_stats']['promotions'],
            "thread_safe": self.enable_thread_safety
        }

    def clear_memory(self):
        """Thread-safe memory clearing."""
        if self._lock:
            with self._lock:
                super().clear_memory()
                logger.info("Memory cleared")
        else:
            super().clear_memory()
            logger.info("Memory cleared")


def get_default_embedding_function() -> Callable[[str], np.ndarray]:
    """
    Get a production-quality embedding function.

    Tries to use sentence-transformers, falls back to warning.

    Returns:
        Embedding function
    """
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading sentence-transformers model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")

        def embed(text: str) -> np.ndarray:
            return model.encode(text, show_progress_bar=False)

        return embed

    except ImportError:
        logger.warning(
            "sentence-transformers not installed. "
            "Using fallback embedding (NOT recommended for production). "
            "Install with: pip install sentence-transformers"
        )

        # Fallback to simple embedding
        def fallback_embed(text: str) -> np.ndarray:
            # Simple word-based embedding
            words = text.lower().split()[:50]  # Limit to 50 words

            # Create fixed-size vector
            embedding = np.zeros(384)

            for i, word in enumerate(words):
                # Hash each word to a position
                hash_val = hash(word) % 384
                embedding[hash_val] += 1.0 / (i + 1)  # Weight by position

            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding

        return fallback_embed


def create_production_agent(
    tier_capacities: List[int] = None,
    max_items: int = 10000,
    embedding_function: Optional[Callable] = None,
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.SEQUENTIAL,
    enable_thread_safety: bool = True,
    log_level: str = "INFO"
) -> ProductionAgent:
    """
    Factory function to create a production-ready agent with sensible defaults.

    Args:
        tier_capacities: List of capacities for each tier (default: [50, 500, 5000])
        max_items: Maximum total items
        embedding_function: Custom embedding function (default: sentence-transformers)
        retrieval_strategy: Retrieval strategy
        enable_thread_safety: Enable thread safety
        log_level: Logging level

    Returns:
        ProductionAgent instance
    """
    if tier_capacities is None:
        tier_capacities = [50, 500, 5000]

    # Validate capacities
    total_capacity = sum(tier_capacities)
    if total_capacity > max_items:
        logger.warning(
            f"Total tier capacity ({total_capacity}) exceeds max_items ({max_items}). "
            f"Adjusting max_items to {total_capacity}"
        )
        max_items = total_capacity

    # Create tier configs
    tier_configs = []
    tier_names = ["L1_fast", "L2_medium", "L3_slow"]
    access_times = [1.0, 10.0, 50.0]
    policies = ["lru", "lfu", "fifo"]

    for i, capacity in enumerate(tier_capacities):
        config = TierConfig(
            name=tier_names[i] if i < len(tier_names) else f"L{i+1}",
            capacity=capacity,
            access_time_ms=access_times[i] if i < len(access_times) else 100.0,
            eviction_policy=policies[i] if i < len(policies) else "lru",
            promotion_threshold=0.6
        )
        tier_configs.append(config)

    # Get embedding function
    if embedding_function is None:
        embedding_function = get_default_embedding_function()

    # Create agent config
    agent_config = AgentConfig(
        tier_configs=tier_configs,
        retrieval_strategy=retrieval_strategy,
        auto_promote=True,
        embedding_function=embedding_function,
        default_top_k=5,
        default_threshold=0.7
    )

    # Create production agent
    agent = ProductionAgent(
        config=agent_config,
        max_items=max_items,
        enable_thread_safety=enable_thread_safety,
        log_level=log_level
    )

    logger.info(
        f"Created production agent with {len(tier_capacities)} tiers, "
        f"max_items={max_items}, thread_safe={enable_thread_safety}"
    )

    return agent
