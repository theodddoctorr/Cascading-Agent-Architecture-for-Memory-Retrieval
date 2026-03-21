"""
Memory tier implementation for cascading architecture.

Provides multi-tier memory storage with configurable access patterns,
capacity limits, and promotion strategies.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import numpy as np
from collections import OrderedDict

from .utils import batch_cosine_similarity, exponential_decay


@dataclass
class TierConfig:
    """Configuration for a memory tier."""

    name: str
    capacity: int = 1000
    access_time_ms: float = 1.0
    eviction_policy: str = "lru"  # lru, lfu, fifo
    promotion_threshold: float = 0.5
    decay_half_life: float = 3600.0  # 1 hour in seconds


class MemoryItem:
    """Represents an item stored in memory."""

    def __init__(
        self,
        content: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_access_time = time.time()
        self.creation_time = time.time()

    def access(self):
        """Record an access to this item."""
        self.access_count += 1
        self.last_access_time = time.time()

    def get_score(self, current_time: Optional[float] = None) -> float:
        """
        Calculate a relevance score based on access patterns.

        Args:
            current_time: Current timestamp (uses time.time() if None)

        Returns:
            Relevance score
        """
        if current_time is None:
            current_time = time.time()

        time_elapsed = current_time - self.last_access_time
        recency_score = exponential_decay(1.0, time_elapsed, 3600.0)
        frequency_score = min(self.access_count / 10.0, 1.0)

        # Weighted combination
        return 0.6 * recency_score + 0.4 * frequency_score


class MemoryTier:
    """
    A single tier in the cascading memory architecture.

    Manages storage, retrieval, and eviction of memory items with
    configurable capacity and access patterns.
    """

    def __init__(self, config: TierConfig):
        """
        Initialize a memory tier.

        Args:
            config: Configuration for this tier
        """
        self.config = config
        self.items: OrderedDict[str, MemoryItem] = OrderedDict()
        self.access_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "promotions": 0
        }

    def add(self, item_id: str, item: MemoryItem) -> Optional[MemoryItem]:
        """
        Add an item to this tier.

        Args:
            item_id: Unique identifier for the item
            item: MemoryItem to add

        Returns:
            Evicted item if capacity exceeded, None otherwise
        """
        evicted = None

        # Check if we need to evict
        if len(self.items) >= self.config.capacity and item_id not in self.items:
            evicted = self._evict_one()

        self.items[item_id] = item

        # Update order for LRU
        if self.config.eviction_policy == "lru":
            self.items.move_to_end(item_id)

        return evicted

    def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        Retrieve an item by ID.

        Args:
            item_id: ID of item to retrieve

        Returns:
            MemoryItem if found, None otherwise
        """
        if item_id in self.items:
            item = self.items[item_id]
            item.access()
            self.access_stats["hits"] += 1

            # Update order for LRU
            if self.config.eviction_policy == "lru":
                self.items.move_to_end(item_id)

            return item
        else:
            self.access_stats["misses"] += 1
            return None

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[tuple]:
        """
        Search for similar items using embedding similarity.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of (item_id, item, similarity) tuples
        """
        if not self.items:
            return []

        # Get all embeddings and IDs
        item_ids = list(self.items.keys())
        embeddings = np.array([
            self.items[item_id].embedding
            for item_id in item_ids
        ])

        # Calculate similarities
        similarities = batch_cosine_similarity(query_embedding, embeddings)

        # Filter by threshold and sort
        results = [
            (item_ids[i], self.items[item_ids[i]], float(similarities[i]))
            for i in range(len(item_ids))
            if similarities[i] >= threshold
        ]

        results.sort(key=lambda x: x[2], reverse=True)

        # Record accesses for top results
        for item_id, item, _ in results[:top_k]:
            item.access()

        return results[:top_k]

    def should_promote(self, item: MemoryItem) -> bool:
        """
        Determine if an item should be promoted to a faster tier.

        Args:
            item: Item to evaluate

        Returns:
            True if item should be promoted
        """
        score = item.get_score()
        return score >= self.config.promotion_threshold

    def _evict_one(self) -> Optional[MemoryItem]:
        """
        Evict one item based on eviction policy.

        Returns:
            Evicted MemoryItem
        """
        if not self.items:
            return None

        if self.config.eviction_policy == "lru":
            # Evict least recently used
            item_id = next(iter(self.items))
            evicted = self.items.pop(item_id)

        elif self.config.eviction_policy == "lfu":
            # Evict least frequently used
            item_id = min(
                self.items.keys(),
                key=lambda k: self.items[k].access_count
            )
            evicted = self.items.pop(item_id)

        elif self.config.eviction_policy == "fifo":
            # Evict oldest
            item_id = min(
                self.items.keys(),
                key=lambda k: self.items[k].creation_time
            )
            evicted = self.items.pop(item_id)

        else:
            raise ValueError(f"Unknown eviction policy: {self.config.eviction_policy}")

        self.access_stats["evictions"] += 1
        return evicted

    def size(self) -> int:
        """Get current number of items in tier."""
        return len(self.items)

    def is_full(self) -> bool:
        """Check if tier is at capacity."""
        return len(self.items) >= self.config.capacity

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for this tier.

        Returns:
            Dictionary of statistics
        """
        hit_rate = 0.0
        total_accesses = self.access_stats["hits"] + self.access_stats["misses"]
        if total_accesses > 0:
            hit_rate = self.access_stats["hits"] / total_accesses

        return {
            "name": self.config.name,
            "size": len(self.items),
            "capacity": self.config.capacity,
            "utilization": len(self.items) / self.config.capacity,
            "hit_rate": hit_rate,
            **self.access_stats
        }

    def clear(self):
        """Clear all items from this tier."""
        self.items.clear()
        self.access_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "promotions": 0
        }
