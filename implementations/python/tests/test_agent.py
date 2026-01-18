"""
Unit tests for agent module.
"""

import unittest
import numpy as np
from cascading_agent import (
    CascadingAgent,
    AgentConfig,
    TierConfig,
    RetrievalStrategy
)


class TestCascadingAgent(unittest.TestCase):
    """Test CascadingAgent class."""

    def setUp(self):
        """Set up test agent."""
        self.config = AgentConfig(
            tier_configs=[
                TierConfig(name="tier1", capacity=10),
                TierConfig(name="tier2", capacity=50)
            ],
            retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
            auto_promote=True,
            default_top_k=5,
            default_threshold=0.7
        )
        self.agent = CascadingAgent(self.config)

    def test_creation(self):
        """Test agent creation."""
        self.assertEqual(len(self.agent.tiers), 2)
        self.assertEqual(self.agent.config.default_top_k, 5)
        self.assertEqual(self.agent.config.default_threshold, 0.7)

    def test_add_content(self):
        """Test adding content to agent."""
        item_id = self.agent.add("Test content", metadata={"type": "test"})

        self.assertIsNotNone(item_id)
        self.assertIsInstance(item_id, str)

        # Check item was added
        stats = self.agent.get_stats()
        self.assertEqual(stats["total_items"], 1)

    def test_add_with_custom_id(self):
        """Test adding content with custom ID."""
        custom_id = "custom_id_123"
        returned_id = self.agent.add("Test", item_id=custom_id)

        self.assertEqual(returned_id, custom_id)

    def test_add_with_precomputed_embedding(self):
        """Test adding content with precomputed embedding."""
        embedding = np.random.rand(384)
        item_id = self.agent.add(
            "Test content",
            embedding=embedding
        )

        self.assertIsNotNone(item_id)

    def test_query(self):
        """Test querying the agent."""
        # Add some content
        self.agent.add("The cascading architecture is efficient")
        self.agent.add("Memory tiers provide fast access")
        self.agent.add("Unrelated content about cooking")

        # Query
        results = self.agent.query("architecture memory systems", top_k=2)

        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 2)

        # Check result format
        if results:
            result = results[0]
            self.assertIn("content", result)
            self.assertIn("similarity", result)
            self.assertIn("tier", result)
            self.assertIn("metadata", result)
            self.assertIn("access_count", result)

    def test_query_with_defaults(self):
        """Test query uses config defaults."""
        self.agent.add("Test content")

        results = self.agent.query("test")

        # Should use default top_k=5 and threshold=0.7
        self.assertLessEqual(len(results), 5)

    def test_query_with_custom_parameters(self):
        """Test query with custom parameters."""
        for i in range(10):
            self.agent.add(f"Document {i}")

        results = self.agent.query(
            "document",
            top_k=3,
            threshold=0.0
        )

        self.assertLessEqual(len(results), 3)

    def test_chat_interface(self):
        """Test chat interface."""
        self.agent.add("Cascading architecture uses multiple tiers")
        self.agent.add("Fast tiers provide quick access")

        response = self.agent.chat(
            message="Tell me about tiers",
            context_k=2
        )

        self.assertIn("message", response)
        self.assertIn("context", response)
        self.assertIn("timestamp", response)
        self.assertEqual(response["message"], "Tell me about tiers")
        self.assertLessEqual(len(response["context"]), 2)

    def test_get_stats(self):
        """Test getting statistics."""
        self.agent.add("Content 1")
        self.agent.add("Content 2")
        self.agent.query("test")

        stats = self.agent.get_stats()

        self.assertIn("query_stats", stats)
        self.assertIn("tier_stats", stats)
        self.assertIn("total_items", stats)
        self.assertEqual(stats["total_items"], 2)
        self.assertGreaterEqual(stats["query_stats"]["total_queries"], 1)

    def test_get_tier_info(self):
        """Test getting tier information."""
        tier_info = self.agent.get_tier_info()

        self.assertEqual(len(tier_info), 2)
        for info in tier_info:
            self.assertIn("name", info)
            self.assertIn("size", info)
            self.assertIn("capacity", info)
            self.assertIn("utilization", info)

    def test_clear_memory(self):
        """Test clearing memory."""
        self.agent.add("Content 1")
        self.agent.add("Content 2")
        self.agent.query("test")

        stats_before = self.agent.get_stats()
        self.assertGreater(stats_before["total_items"], 0)

        self.agent.clear_memory()

        stats_after = self.agent.get_stats()
        self.assertEqual(stats_after["total_items"], 0)
        self.assertEqual(len(self.agent.conversation_history), 0)

    def test_export_import_memory(self):
        """Test exporting and importing memory."""
        # Add content
        self.agent.add("Content 1", metadata={"key": "value1"})
        self.agent.add("Content 2", metadata={"key": "value2"})

        # Export
        exported = self.agent.export_memory()

        self.assertEqual(len(exported), 2)
        self.assertIn("content", exported[0])
        self.assertIn("embedding", exported[0])
        self.assertIn("metadata", exported[0])

        # Create new agent
        new_agent = CascadingAgent(self.config)
        self.assertEqual(new_agent.get_stats()["total_items"], 0)

        # Import
        new_agent.import_memory(exported)

        self.assertEqual(new_agent.get_stats()["total_items"], 2)

    def test_conversation_history(self):
        """Test conversation history tracking."""
        self.agent.add("Test content")

        # Perform queries
        self.agent.query("query 1")
        self.agent.query("query 2")

        self.assertEqual(len(self.agent.conversation_history), 2)

        entry = self.agent.conversation_history[0]
        self.assertIn("timestamp", entry)
        self.assertIn("query", entry)
        self.assertIn("results_count", entry)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.agent)

        self.assertIn("CascadingAgent", repr_str)
        self.assertIn("tiers=2", repr_str)

    def test_custom_embedding_function(self):
        """Test using custom embedding function."""
        def custom_embedding(text: str) -> np.ndarray:
            # Simple length-based embedding
            return np.array([len(text)] * 10, dtype=float)

        config = AgentConfig(
            tier_configs=[TierConfig(name="tier1", capacity=10)],
            embedding_function=custom_embedding
        )

        agent = CascadingAgent(config)
        agent.add("Test")

        # Should use custom embedding
        stats = agent.get_stats()
        self.assertEqual(stats["total_items"], 1)


if __name__ == "__main__":
    unittest.main()
