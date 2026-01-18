"""
Cascading retrieval implementation.

Orchestrates search across multiple memory tiers with automatic
promotion and optimization.
"""

import time
from enum import Enum
from typing import List, Optional, Dict, Any
import numpy as np

from .memory_tier import MemoryTier, MemoryItem, TierConfig


class RetrievalStrategy(Enum):
    """Strategy for cascading retrieval."""

    SEQUENTIAL = "sequential"  # Try each tier in order
    PARALLEL = "parallel"  # Query all tiers simultaneously
    ADAPTIVE = "adaptive"  # Adapt based on query characteristics


class CascadingRetrieval:
    """
    Manages cascading retrieval across multiple memory tiers.

    Implements intelligent search strategies, automatic promotion,
    and optimization of access patterns.
    """

    def __init__(
        self,
        tiers: List[MemoryTier],
        strategy: RetrievalStrategy = RetrievalStrategy.SEQUENTIAL,
        auto_promote: bool = True
    ):
        """
        Initialize cascading retrieval system.

        Args:
            tiers: List of MemoryTier objects, ordered from fastest to slowest
            strategy: Retrieval strategy to use
            auto_promote: Automatically promote frequently accessed items
        """
        self.tiers = tiers
        self.strategy = strategy
        self.auto_promote = auto_promote
        self.query_stats = {
            "total_queries": 0,
            "tier_hits": {tier.config.name: 0 for tier in tiers},
            "avg_latency_ms": 0.0,
            "promotions": 0
        }

    def retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.7,
        max_tiers: Optional[int] = None
    ) -> List[tuple]:
        """
        Retrieve items using cascading search across tiers.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            max_tiers: Maximum number of tiers to search (None for all)

        Returns:
            List of (item_id, item, similarity, tier_name) tuples
        """
        start_time = time.time()
        self.query_stats["total_queries"] += 1

        if self.strategy == RetrievalStrategy.SEQUENTIAL:
            results = self._sequential_retrieve(
                query_embedding, top_k, threshold, max_tiers
            )
        elif self.strategy == RetrievalStrategy.PARALLEL:
            results = self._parallel_retrieve(
                query_embedding, top_k, threshold, max_tiers
            )
        elif self.strategy == RetrievalStrategy.ADAPTIVE:
            results = self._adaptive_retrieve(
                query_embedding, top_k, threshold, max_tiers
            )
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Auto-promote frequently accessed items
        if self.auto_promote and results:
            self._promote_items(results)

        # Update stats
        latency_ms = (time.time() - start_time) * 1000
        self._update_latency_stats(latency_ms)

        return results

    def _sequential_retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        threshold: float,
        max_tiers: Optional[int]
    ) -> List[tuple]:
        """
        Sequential retrieval: try each tier in order until enough results found.

        Args:
            query_embedding: Query vector
            top_k: Number of results needed
            threshold: Similarity threshold
            max_tiers: Max tiers to search

        Returns:
            List of results
        """
        all_results = []
        tiers_to_search = self.tiers[:max_tiers] if max_tiers else self.tiers

        for tier in tiers_to_search:
            # Simulate access time
            time.sleep(tier.config.access_time_ms / 1000.0)

            tier_results = tier.search(query_embedding, top_k, threshold)

            if tier_results:
                self.query_stats["tier_hits"][tier.config.name] += 1

                # Add tier name to results
                tier_results = [
                    (item_id, item, sim, tier.config.name)
                    for item_id, item, sim in tier_results
                ]
                all_results.extend(tier_results)

                # If we have enough results, stop cascading
                if len(all_results) >= top_k:
                    break

        # Sort all results and return top-k
        all_results.sort(key=lambda x: x[2], reverse=True)
        return all_results[:top_k]

    def _parallel_retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        threshold: float,
        max_tiers: Optional[int]
    ) -> List[tuple]:
        """
        Parallel retrieval: query all tiers simultaneously.

        Args:
            query_embedding: Query vector
            top_k: Number of results needed
            threshold: Similarity threshold
            max_tiers: Max tiers to search

        Returns:
            List of results
        """
        all_results = []
        tiers_to_search = self.tiers[:max_tiers] if max_tiers else self.tiers

        # In a real implementation, this would use threading/asyncio
        # For now, we simulate by querying all tiers
        max_access_time = 0.0

        for tier in tiers_to_search:
            max_access_time = max(max_access_time, tier.config.access_time_ms)
            tier_results = tier.search(query_embedding, top_k, threshold)

            if tier_results:
                self.query_stats["tier_hits"][tier.config.name] += 1
                tier_results = [
                    (item_id, item, sim, tier.config.name)
                    for item_id, item, sim in tier_results
                ]
                all_results.extend(tier_results)

        # Simulate parallel access (wait for slowest tier)
        time.sleep(max_access_time / 1000.0)

        # Deduplicate and sort
        seen = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x[2], reverse=True):
            item_id = result[0]
            if item_id not in seen:
                seen.add(item_id)
                unique_results.append(result)

        return unique_results[:top_k]

    def _adaptive_retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        threshold: float,
        max_tiers: Optional[int]
    ) -> List[tuple]:
        """
        Adaptive retrieval: choose strategy based on query characteristics.

        Args:
            query_embedding: Query vector
            top_k: Number of results needed
            threshold: Similarity threshold
            max_tiers: Max tiers to search

        Returns:
            List of results
        """
        # Simple heuristic: use parallel for high threshold (specific queries),
        # sequential for low threshold (broad queries)
        if threshold >= 0.8:
            return self._parallel_retrieve(
                query_embedding, top_k, threshold, max_tiers
            )
        else:
            return self._sequential_retrieve(
                query_embedding, top_k, threshold, max_tiers
            )

    def _promote_items(self, results: List[tuple]):
        """
        Promote frequently accessed items to faster tiers.

        Args:
            results: Retrieved results to consider for promotion
        """
        for item_id, item, similarity, source_tier_name in results:
            # Find source tier
            source_tier_idx = None
            for idx, tier in enumerate(self.tiers):
                if tier.config.name == source_tier_name:
                    source_tier_idx = idx
                    break

            if source_tier_idx is None or source_tier_idx == 0:
                continue  # Already in fastest tier or not found

            source_tier = self.tiers[source_tier_idx]

            # Check if should promote
            if source_tier.should_promote(item):
                # Try to promote to faster tier
                target_tier = self.tiers[source_tier_idx - 1]

                if not target_tier.is_full() or True:  # Always try promotion
                    # Add to faster tier (may evict something)
                    target_tier.add(item_id, item)

                    # Optionally remove from slower tier
                    # (or keep for redundancy - implementation choice)
                    # source_tier.items.pop(item_id, None)

                    source_tier.access_stats["promotions"] += 1
                    self.query_stats["promotions"] += 1

    def add_item(
        self,
        item_id: str,
        content: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
        target_tier: int = -1
    ):
        """
        Add an item to the memory system.

        Args:
            item_id: Unique identifier
            content: Item content
            embedding: Vector embedding
            metadata: Optional metadata
            target_tier: Tier index to add to (-1 for slowest)
        """
        item = MemoryItem(content, embedding, metadata)

        if target_tier == -1:
            target_tier = len(self.tiers) - 1

        self.tiers[target_tier].add(item_id, item)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the retrieval system.

        Returns:
            Dictionary of statistics
        """
        tier_stats = [tier.get_stats() for tier in self.tiers]

        return {
            "query_stats": self.query_stats,
            "tier_stats": tier_stats,
            "total_items": sum(tier.size() for tier in self.tiers)
        }

    def _update_latency_stats(self, latency_ms: float):
        """Update average latency statistics."""
        n = self.query_stats["total_queries"]
        current_avg = self.query_stats["avg_latency_ms"]

        # Incremental average
        new_avg = current_avg + (latency_ms - current_avg) / n
        self.query_stats["avg_latency_ms"] = new_avg

    def clear_all_tiers(self):
        """Clear all memory tiers."""
        for tier in self.tiers:
            tier.clear()

        self.query_stats = {
            "total_queries": 0,
            "tier_hits": {tier.config.name: 0 for tier in self.tiers},
            "avg_latency_ms": 0.0,
            "promotions": 0
        }
