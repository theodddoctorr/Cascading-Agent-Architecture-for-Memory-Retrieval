"""
Advanced retrieval example demonstrating:
- Different retrieval strategies
- Custom embeddings
- Memory export/import
- Performance comparison
"""

import time
import numpy as np
from cascading_agent import (
    CascadingAgent,
    AgentConfig,
    TierConfig,
    RetrievalStrategy
)


def simple_sentence_embedding(text: str) -> np.ndarray:
    """
    Simple word-based embedding for demonstration.

    In production, use proper models like:
    - sentence-transformers
    - OpenAI embeddings
    - Cohere embeddings
    """
    # Normalize text
    words = text.lower().split()

    # Create simple bag-of-words vector
    # Using a small vocabulary for demo
    vocab = {
        'cascading': 0, 'agent': 1, 'memory': 2, 'retrieval': 3,
        'tier': 4, 'fast': 5, 'slow': 6, 'search': 7,
        'query': 8, 'performance': 9, 'efficient': 10, 'data': 11,
        'storage': 12, 'cache': 13, 'system': 14, 'architecture': 15
    }

    # Initialize embedding
    embedding = np.zeros(len(vocab) * 3)  # Dimension: 48

    # Simple word presence
    for word in words:
        if word in vocab:
            idx = vocab[word]
            embedding[idx] = 1.0
            # Add some randomness for variation
            embedding[idx + len(vocab)] = np.random.rand() * 0.5
            embedding[idx + len(vocab) * 2] = len(word) / 10.0

    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    return embedding


def compare_strategies():
    """Compare different retrieval strategies."""
    print("\n" + "=" * 70)
    print("Comparing Retrieval Strategies")
    print("=" * 70 + "\n")

    tier_configs = [
        TierConfig(name="L1", capacity=5, access_time_ms=1.0),
        TierConfig(name="L2", capacity=20, access_time_ms=10.0),
        TierConfig(name="L3", capacity=100, access_time_ms=50.0)
    ]

    strategies = [
        RetrievalStrategy.SEQUENTIAL,
        RetrievalStrategy.PARALLEL,
        RetrievalStrategy.ADAPTIVE
    ]

    # Test data
    documents = [
        "Cascading memory architecture for efficient retrieval",
        "Multi-tier storage system with automatic promotion",
        "Fast cache for frequently accessed data",
        "Slow storage for long-term memory retention",
        "Query optimization across memory tiers",
        "Semantic search using vector embeddings",
        "Performance tuning for agent systems",
        "Scalable architecture for large datasets"
    ]

    results = {}

    for strategy in strategies:
        print(f"\nTesting {strategy.value} strategy:")

        # Create agent with custom embedding
        config = AgentConfig(
            tier_configs=tier_configs,
            retrieval_strategy=strategy,
            embedding_function=simple_sentence_embedding,
            auto_promote=True
        )
        agent = CascadingAgent(config)

        # Add documents
        for doc in documents:
            agent.add(content=doc)

        # Perform queries
        queries = [
            "memory storage systems",
            "fast cache performance",
            "semantic search queries"
        ]

        start_time = time.time()
        query_results = []

        for query in queries:
            qr = agent.query(query, top_k=3, threshold=0.1)
            query_results.append(qr)

        elapsed = (time.time() - start_time) * 1000

        # Get stats
        stats = agent.get_stats()

        results[strategy.value] = {
            "elapsed_ms": elapsed,
            "avg_latency": stats['query_stats']['avg_latency_ms'],
            "total_queries": stats['query_stats']['total_queries'],
            "results": query_results
        }

        print(f"  Elapsed time: {elapsed:.2f}ms")
        print(f"  Avg latency: {stats['query_stats']['avg_latency_ms']:.2f}ms")
        print(f"  Tier hits: {stats['query_stats']['tier_hits']}")

    print("\n" + "-" * 70)
    print("Strategy Comparison Summary:")
    print("-" * 70)
    for strategy_name, data in results.items():
        print(f"{strategy_name:12s}: {data['elapsed_ms']:6.2f}ms total, "
              f"{data['avg_latency']:5.2f}ms avg")


def demonstrate_export_import():
    """Demonstrate memory export and import."""
    print("\n" + "=" * 70)
    print("Memory Export/Import Example")
    print("=" * 70 + "\n")

    # Create first agent
    print("Creating first agent and adding data...")
    config1 = AgentConfig(
        tier_configs=[
            TierConfig(name="tier1", capacity=50),
            TierConfig(name="tier2", capacity=200)
        ],
        embedding_function=simple_sentence_embedding
    )
    agent1 = CascadingAgent(config1)

    # Add data
    for i in range(10):
        agent1.add(f"Document {i}: Important information about topic {i}")

    print(f"  Agent 1 has {sum(t.size() for t in agent1.tiers)} items")

    # Export memory
    print("\nExporting memory...")
    exported = agent1.export_memory()
    print(f"  Exported {len(exported)} items")

    # Create second agent
    print("\nCreating second agent...")
    agent2 = CascadingAgent(config1)
    print(f"  Agent 2 has {sum(t.size() for t in agent2.tiers)} items (empty)")

    # Import memory
    print("\nImporting memory to second agent...")
    agent2.import_memory(exported)
    print(f"  Agent 2 now has {sum(t.size() for t in agent2.tiers)} items")

    # Verify
    print("\nVerifying imported data...")
    results = agent2.query("information about topic", top_k=5)
    print(f"  Query found {len(results)} results:")
    for r in results[:3]:
        print(f"    - {r['content'][:50]}...")


def demonstrate_custom_tiers():
    """Demonstrate custom tier configurations."""
    print("\n" + "=" * 70)
    print("Custom Tier Configuration Example")
    print("=" * 70 + "\n")

    # Create a 4-tier system mimicking CPU cache hierarchy
    tier_configs = [
        TierConfig(
            name="L1_Cache",
            capacity=8,
            access_time_ms=0.5,
            eviction_policy="lru",
            promotion_threshold=0.8
        ),
        TierConfig(
            name="L2_Cache",
            capacity=32,
            access_time_ms=2.0,
            eviction_policy="lru",
            promotion_threshold=0.6
        ),
        TierConfig(
            name="L3_Cache",
            capacity=128,
            access_time_ms=10.0,
            eviction_policy="lfu",
            promotion_threshold=0.4
        ),
        TierConfig(
            name="Main_Memory",
            capacity=1000,
            access_time_ms=50.0,
            eviction_policy="fifo",
            promotion_threshold=0.2
        )
    ]

    config = AgentConfig(
        tier_configs=tier_configs,
        retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
        embedding_function=simple_sentence_embedding,
        auto_promote=True
    )

    agent = CascadingAgent(config)

    print("Created 4-tier agent:")
    for tier in agent.tiers:
        print(f"  {tier.config.name:15s}: "
              f"capacity={tier.config.capacity:4d}, "
              f"latency={tier.config.access_time_ms:5.1f}ms, "
              f"policy={tier.config.eviction_policy}")

    # Add data
    print("\nAdding 50 documents...")
    for i in range(50):
        agent.add(f"Article {i} about memory systems and caching strategies")

    # Perform multiple queries to trigger promotions
    print("\nPerforming queries to test auto-promotion...")
    for _ in range(5):
        agent.query("memory caching strategies", top_k=3)

    # Show tier distribution
    print("\nTier distribution after queries:")
    tier_info = agent.get_tier_info()
    for info in tier_info:
        print(f"  {info['name']:15s}: {info['size']:3d}/{info['capacity']:4d} items "
              f"({info['utilization']:5.1%}), "
              f"promotions={info['promotions']}")


def main():
    """Run all advanced examples."""
    print("\n" + "=" * 70)
    print("Advanced Cascading Agent Examples")
    print("=" * 70)

    compare_strategies()
    demonstrate_export_import()
    demonstrate_custom_tiers()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
