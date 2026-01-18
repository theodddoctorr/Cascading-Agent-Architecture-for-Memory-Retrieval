"""
Unit tests for memory_tier module.
"""

import unittest
import numpy as np
import time
from cascading_agent.memory_tier import MemoryTier, TierConfig, MemoryItem


class TestMemoryItem(unittest.TestCase):
    """Test MemoryItem class."""

    def test_creation(self):
        """Test MemoryItem creation."""
        embedding = np.random.rand(384)
        item = MemoryItem(
            content="Test content",
            embedding=embedding,
            metadata={"key": "value"}
        )

        self.assertEqual(item.content, "Test content")
        self.assertTrue(np.array_equal(item.embedding, embedding))
        self.assertEqual(item.metadata["key"], "value")
        self.assertEqual(item.access_count, 0)

    def test_access_tracking(self):
        """Test access count tracking."""
        item = MemoryItem("Test", np.random.rand(384))

        initial_time = item.last_access_time
        time.sleep(0.01)

        item.access()
        self.assertEqual(item.access_count, 1)
        self.assertGreater(item.last_access_time, initial_time)

        item.access()
        self.assertEqual(item.access_count, 2)

    def test_score_calculation(self):
        """Test relevance score calculation."""
        item = MemoryItem("Test", np.random.rand(384))

        # Fresh item should have high score
        score1 = item.get_score()
        self.assertGreater(score1, 0.5)

        # After multiple accesses
        for _ in range(5):
            item.access()

        score2 = item.get_score()
        self.assertGreater(score2, score1)


class TestMemoryTier(unittest.TestCase):
    """Test MemoryTier class."""

    def setUp(self):
        """Set up test tier."""
        self.config = TierConfig(
            name="test_tier",
            capacity=10,
            access_time_ms=1.0,
            eviction_policy="lru"
        )
        self.tier = MemoryTier(self.config)

    def test_add_item(self):
        """Test adding items to tier."""
        item = MemoryItem("Test", np.random.rand(384))
        evicted = self.tier.add("item1", item)

        self.assertIsNone(evicted)  # No eviction yet
        self.assertEqual(self.tier.size(), 1)
        self.assertIn("item1", self.tier.items)

    def test_capacity_limit(self):
        """Test that capacity is enforced."""
        # Fill to capacity
        for i in range(10):
            item = MemoryItem(f"Item {i}", np.random.rand(384))
            self.tier.add(f"item{i}", item)

        self.assertEqual(self.tier.size(), 10)
        self.assertTrue(self.tier.is_full())

        # Add one more - should evict
        item = MemoryItem("Item 11", np.random.rand(384))
        evicted = self.tier.add("item11", item)

        self.assertIsNotNone(evicted)
        self.assertEqual(self.tier.size(), 10)

    def test_get_item(self):
        """Test retrieving items."""
        item = MemoryItem("Test", np.random.rand(384))
        self.tier.add("item1", item)

        retrieved = self.tier.get("item1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "Test")
        self.assertEqual(retrieved.access_count, 1)

        # Non-existent item
        missing = self.tier.get("nonexistent")
        self.assertIsNone(missing)

    def test_search(self):
        """Test similarity search."""
        # Add items with known embeddings
        embeddings = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ]

        for i, emb in enumerate(embeddings):
            item = MemoryItem(f"Item {i}", emb)
            self.tier.add(f"item{i}", item)

        # Query should match first item best
        query = np.array([0.9, 0.1, 0.0])
        results = self.tier.search(query, top_k=2, threshold=0.0)

        self.assertEqual(len(results), 2)
        # First result should be item0
        self.assertEqual(results[0][0], "item0")
        self.assertGreater(results[0][2], results[1][2])  # Higher similarity

    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        config = TierConfig(
            name="lru_tier",
            capacity=3,
            eviction_policy="lru"
        )
        tier = MemoryTier(config)

        # Add 3 items
        for i in range(3):
            item = MemoryItem(f"Item {i}", np.random.rand(384))
            tier.add(f"item{i}", item)

        # Access item0 to make it more recent
        tier.get("item0")

        # Add 4th item - should evict item1 (least recently used)
        item = MemoryItem("Item 3", np.random.rand(384))
        tier.add("item3", item)

        self.assertIsNone(tier.get("item1"))  # Evicted
        self.assertIsNotNone(tier.get("item0"))  # Still there
        self.assertIsNotNone(tier.get("item3"))  # Newly added

    def test_statistics(self):
        """Test statistics tracking."""
        item = MemoryItem("Test", np.random.rand(384))
        self.tier.add("item1", item)

        # Hit
        self.tier.get("item1")
        # Miss
        self.tier.get("nonexistent")

        stats = self.tier.get_stats()

        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["size"], 1)
        self.assertAlmostEqual(stats["hit_rate"], 0.5)

    def test_clear(self):
        """Test clearing tier."""
        for i in range(5):
            item = MemoryItem(f"Item {i}", np.random.rand(384))
            self.tier.add(f"item{i}", item)

        self.assertEqual(self.tier.size(), 5)

        self.tier.clear()

        self.assertEqual(self.tier.size(), 0)
        self.assertEqual(self.tier.access_stats["hits"], 0)


if __name__ == "__main__":
    unittest.main()
