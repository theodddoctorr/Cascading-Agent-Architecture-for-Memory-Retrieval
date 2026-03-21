"""
Basic usage example for the Cascading Agent Architecture.

This example demonstrates:
- Creating a simple cascading agent
- Adding content to memory
- Querying the memory system
- Viewing statistics
"""

import numpy as np
from cascading_agent import CascadingAgent, AgentConfig, TierConfig, RetrievalStrategy


def main():
    print("=" * 70)
    print("Cascading Agent Architecture - Basic Usage Example")
    print("=" * 70)
    print()

    # Step 1: Configure memory tiers
    print("Step 1: Configuring memory tiers...")
    tier_configs = [
        TierConfig(
            name="fast_cache",
            capacity=10,
            access_time_ms=1.0,
            eviction_policy="lru"
        ),
        TierConfig(
            name="medium_storage",
            capacity=50,
            access_time_ms=10.0,
            eviction_policy="lfu"
        ),
        TierConfig(
            name="slow_storage",
            capacity=1000,
            access_time_ms=100.0,
            eviction_policy="fifo"
        )
    ]
    print(f"  Created {len(tier_configs)} tiers:")
    for tc in tier_configs:
        print(f"    - {tc.name}: capacity={tc.capacity}, latency={tc.access_time_ms}ms")
    print()

    # Step 2: Create agent
    print("Step 2: Creating cascading agent...")
    config = AgentConfig(
        tier_configs=tier_configs,
        retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
        auto_promote=True,
        default_top_k=5,
        default_threshold=0.5
    )
    agent = CascadingAgent(config)
    print(f"  Agent created: {agent}")
    print()

    # Step 3: Add content to memory
    print("Step 3: Adding content to memory...")
    documents = [
        "The cascading architecture provides efficient multi-tier memory retrieval.",
        "Agents can access fast cache for frequently used information.",
        "Slower storage tiers hold less frequently accessed data.",
        "Automatic promotion moves popular items to faster tiers.",
        "Memory tiers have configurable capacity and eviction policies.",
        "The system optimizes for both speed and storage efficiency.",
        "Query performance improves as access patterns are learned.",
        "Embeddings enable semantic similarity search across tiers.",
        "The architecture scales to large knowledge bases.",
        "Context-aware retrieval enhances agent responses."
    ]

    for doc in documents:
        item_id = agent.add(content=doc, metadata={"type": "documentation"})
        print(f"  Added: {doc[:50]}... (ID: {item_id})")
    print()

    # Step 4: Query the memory system
    print("Step 4: Querying the memory system...")
    query = "How does the cascading architecture work?"
    print(f"  Query: '{query}'")
    print()

    results = agent.query(query=query, top_k=3, threshold=0.3)

    print(f"  Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  Result {i}:")
        print(f"    Content: {result['content']}")
        print(f"    Similarity: {result['similarity']:.4f}")
        print(f"    Tier: {result['tier']}")
        print(f"    Access count: {result['access_count']}")
    print()

    # Step 5: Query again (should use promoted items)
    print("Step 5: Querying again (testing auto-promotion)...")
    results2 = agent.query(query=query, top_k=3, threshold=0.3)
    print(f"  Found {len(results2)} results from faster tiers")
    print()

    # Step 6: View statistics
    print("Step 6: Viewing system statistics...")
    stats = agent.get_stats()

    print(f"\n  Query Statistics:")
    print(f"    Total queries: {stats['query_stats']['total_queries']}")
    print(f"    Avg latency: {stats['query_stats']['avg_latency_ms']:.2f}ms")
    print(f"    Promotions: {stats['query_stats']['promotions']}")

    print(f"\n  Tier Statistics:")
    for tier_stat in stats['tier_stats']:
        print(f"    {tier_stat['name']}:")
        print(f"      Size: {tier_stat['size']}/{tier_stat['capacity']}")
        print(f"      Utilization: {tier_stat['utilization']:.1%}")
        print(f"      Hit rate: {tier_stat['hit_rate']:.2%}")
        print(f"      Hits: {tier_stat['hits']}, Misses: {tier_stat['misses']}")
    print()

    # Step 7: Test chat interface
    print("Step 7: Testing chat interface...")
    response = agent.chat(
        message="Tell me about memory tiers",
        context_k=2,
        threshold=0.3
    )

    print(f"  Message: {response['message']}")
    print(f"  Retrieved {len(response['context'])} context items:")
    for ctx in response['context']:
        print(f"    - {ctx['content'][:60]}... (sim: {ctx['similarity']:.3f})")
    print()

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
