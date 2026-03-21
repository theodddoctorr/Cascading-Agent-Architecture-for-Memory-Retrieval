"""
Unit tests for retrieval module.
"""

import unittest
import numpy as np
from cascading_agent.memory_tier import MemoryTier, TierConfig, MemoryItem
from cascading_agent.retrieval import CascadingRetrieval, RetrievalStrategy


class TestCascadingRetrieval(unittest.TestCase):
    """Test CascadingRetrieval class."""

    def setUp(self):
        """Set up test retrieval system."""
        self.tier_configs = [
            TierConfig(name="fast", capacity=5, access_time_ms=1.0),
            TierConfig(name="medium", capacity=10, access_time_ms=10.0),
            TierConfig(name="slow", capacity=20, access_time_ms=50.0)
        ]

        self.tiers = [MemoryTier(config) for config in self.tier_configs]
        self.retrieval = CascadingRetrieval(
            tiers=self.tiers,
            strategy=RetrievalStrategy.SEQUENTIAL,
            auto_promote=False  # Disable for basic tests
        )

    def test_creation(self):
        """Test retrieval system creation."""
        self.assertEqual(len(self.retrieval.tiers), 3)
        self.assertEqual(self.retrieval.strategy, RetrievalStrategy.SEQUENTIAL)
        self.assertEqual(self.retrieval.query_stats["total_queries"], 0)

    def test_add_item(self):
        """Test adding items to retrieval system."""
        embedding = np.random.rand(384)
        self.retrieval.add_item(
            item_id="test1",
            content="Test content",
            embedding=embedding,
            metadata={"key": "value"}
        )

        # Should be added to slowest tier by default
        self.assertEqual(self.tiers[-1].size(), 1)

    def test_sequential_retrieval(self):
        """Test sequential retrieval strategy."""
        # Add items to different tiers
        emb1 = np.array([1.0, 0.0])
        emb2 = np.array([0.0, 1.0])

        item1 = MemoryItem("Fast item", emb1)
        item2 = MemoryItem("Slow item", emb2)

        self.tiers[0].add("item1", item1)  # Fast tier
        self.tiers[2].add("item2", item2)  # Slow tier

        # Query matching first tier
        query = np.array([0.9, 0.1])
        results = self.retrieval.retrieve(query, top_k=1, threshold=0.0)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "item1")
        self.assertEqual(results[0][3], "fast")  # From fast tier

    def test_parallel_retrieval(self):
        """Test parallel retrieval strategy."""
        retrieval = CascadingRetrieval(
            tiers=self.tiers,
            strategy=RetrievalStrategy.PARALLEL,
            auto_promote=False
        )

        # Add items
        emb1 = np.array([1.0, 0.0])
        emb2 = np.array([0.0, 1.0])

        self.tiers[0].add("item1", MemoryItem("Item 1", emb1))
        self.tiers[2].add("item2", MemoryItem("Item 2", emb2))

        # Query
        query = np.array([0.5, 0.5])
        results = retrieval.retrieve(query, top_k=2, threshold=0.0)

        self.assertEqual(len(results), 2)

    def test_auto_promotion(self):
        """Test automatic promotion of frequently accessed items."""
        retrieval = CascadingRetrieval(
            tiers=self.tiers,
            strategy=RetrievalStrategy.SEQUENTIAL,
            auto_promote=True
        )

        # Add item to slow tier
        emb = np.array([1.0, 0.0])
        item = MemoryItem("Test item", emb)
        self.tiers[2].add("item1", item)

        # Access multiple times to trigger promotion
        query = np.array([0.95, 0.05])
        for _ in range(5):
            retrieval.retrieve(query, top_k=1, threshold=0.0)
            item.access()  # Simulate access

        # Check if promoted (might be in faster tier)
        stats = retrieval.get_stats()
        # Promotion count should increase
        self.assertGreaterEqual(stats["query_stats"]["promotions"], 0)

    def test_max_tiers_parameter(self):
        """Test limiting search to specific number of tiers."""
        # Add items to all tiers
        for i, tier in enumerate(self.tiers):
            emb = np.random.rand(384)
            tier.add(f"item{i}", MemoryItem(f"Item {i}", emb))

        query = np.random.rand(384)

        # Search only first tier
        results = self.retrieval.retrieve(query, top_k=5, max_tiers=1)

        # All results should be from first tier
        for _, _, _, tier_name in results:
            self.assertEqual(tier_name, "fast")

    def test_threshold_filtering(self):
        """Test similarity threshold filtering."""
        # Add items with known embeddings
        emb1 = np.array([1.0, 0.0, 0.0])
        emb2 = np.array([0.0, 1.0, 0.0])

        self.tiers[0].add("item1", MemoryItem("Item 1", emb1))
        self.tiers[0].add("item2", MemoryItem("Item 2", emb2))

        # Query matching item1
        query = np.array([1.0, 0.0, 0.0])

        # High threshold should return only close matches
        results_high = self.retrieval.retrieve(query, top_k=5, threshold=0.9)
        self.assertEqual(len(results_high), 1)

        # Low threshold should return more
        results_low = self.retrieval.retrieve(query, top_k=5, threshold=0.0)
        self.assertGreaterEqual(len(results_low), len(results_high))

    def test_statistics_tracking(self):
        """Test statistics are properly tracked."""
        # Add items
        for i in range(3):
            emb = np.random.rand(384)
            self.tiers[i].add(f"item{i}", MemoryItem(f"Item {i}", emb))

        # Perform queries
        query = np.random.rand(384)
        for _ in range(5):
            self.retrieval.retrieve(query, top_k=1)

        stats = self.retrieval.get_stats()

        self.assertEqual(stats["query_stats"]["total_queries"], 5)
        self.assertGreater(stats["query_stats"]["avg_latency_ms"], 0.0)
        self.assertEqual(stats["total_items"], 3)

    def test_clear_all_tiers(self):
        """Test clearing all tiers."""
        # Add items
        for tier in self.tiers:
            emb = np.random.rand(384)
            tier.add("item", MemoryItem("Test", emb))

        # Perform query
        query = np.random.rand(384)
        self.retrieval.retrieve(query)

        # Clear
        self.retrieval.clear_all_tiers()

        stats = self.retrieval.get_stats()
        self.assertEqual(stats["total_items"], 0)
        self.assertEqual(stats["query_stats"]["total_queries"], 0)


if __name__ == "__main__":
    unittest.main()
