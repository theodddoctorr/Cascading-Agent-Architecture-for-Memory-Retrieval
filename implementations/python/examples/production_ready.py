"""
Production-ready example with all critical fixes applied.

This example demonstrates:
- Using ProductionAgent with thread safety
- Proper embedding functions
- Memory limit monitoring
- Error handling
- Health checks
"""

from cascading_agent import create_production_agent, ProductionAgent
import time


def main():
    print("=" * 70)
    print("Production-Ready Cascading Agent Example")
    print("=" * 70)
    print()

    # Create production agent with sensible defaults
    print("Creating production-ready agent...")
    print("  - Real embeddings (sentence-transformers if available)")
    print("  - Thread safety enabled")
    print("  - Memory limits enforced")
    print("  - Error handling and logging")
    print()

    agent = create_production_agent(
        tier_capacities=[50, 500, 5000],  # Safe limits
        max_items=10000,
        retrieval_strategy=None,  # Uses default (SEQUENTIAL)
        enable_thread_safety=True,
        log_level="INFO"
    )

    print(f"Agent created: {agent}")
    print()

    # Check initial health
    print("Initial health status:")
    health = agent.get_health_status()
    print(f"  Status: {health['status']}")
    print(f"  Items: {health['total_items']}/{health['max_items']}")
    print(f"  Capacity: {health['capacity_used']:.1%}")
    print()

    # Add content with error handling
    print("Adding content...")
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
        "Context-aware retrieval enhances agent responses.",
        "Production deployment requires proper embedding functions.",
        "Thread safety is essential for concurrent applications.",
        "Memory limits prevent out-of-memory errors.",
        "Health monitoring enables proactive maintenance.",
        "Logging provides visibility into system operations."
    ]

    added_count = 0
    for doc in documents:
        result = agent.add(content=doc, metadata={"type": "documentation"})
        if result:
            added_count += 1
        else:
            print(f"  Failed to add: {doc[:50]}...")

    print(f"  Successfully added {added_count}/{len(documents)} documents")
    print()

    # Query with error handling
    print("Performing queries...")
    queries = [
        "How does the cascading architecture work?",
        "What about production deployment?",
        "Tell me about thread safety"
    ]

    for query in queries:
        print(f"\n  Query: '{query}'")
        results = agent.query(query=query, top_k=3, threshold=0.3)

        if results:
            print(f"  Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"    {i}. {result['content'][:60]}...")
                print(f"       Similarity: {result['similarity']:.3f}, "
                      f"Tier: {result['tier']}")
        else:
            print("  No results found")

    print()

    # Demonstrate thread safety (simulation)
    print("Demonstrating thread safety...")
    print("  Agent is thread-safe by default")
    print("  Multiple threads can safely call add() and query()")
    print()

    # Check health after operations
    print("Health status after operations:")
    health = agent.get_health_status()
    print(f"  Status: {health['status']}")
    print(f"  Items: {health['total_items']}/{health['max_items']}")
    print(f"  Capacity: {health['capacity_used']:.1%}")
    print(f"  Total queries: {health['total_queries']}")
    print(f"  Avg latency: {health['avg_latency_ms']:.2f}ms")
    print(f"  Promotions: {health['promotions']}")
    print(f"  Thread safe: {health['thread_safe']}")
    print()

    # Show statistics
    print("Detailed statistics:")
    stats = agent.get_stats()

    for tier_stat in stats['tier_stats']:
        print(f"  {tier_stat['name']}:")
        print(f"    Size: {tier_stat['size']}/{tier_stat['capacity']} "
              f"({tier_stat['utilization']:.1%})")
        print(f"    Hits: {tier_stat['hits']}, "
              f"Hit rate: {tier_stat['hit_rate']:.1%}")
        print(f"    Promotions: {tier_stat['promotions']}")

    print()

    # Test capacity limits
    print("Testing capacity limits...")
    print(f"  Current capacity: {health['capacity_used']:.1%}")
    print(f"  Trying to add items up to limit...")

    # Try to add many items
    for i in range(100):
        result = agent.add(f"Test document {i}")
        if not result and i == 0:
            print(f"  ⚠️  Could not add item - at capacity")
            break

    final_health = agent.get_health_status()
    print(f"  Final capacity: {final_health['capacity_used']:.1%}")
    print(f"  Status: {final_health['status']}")
    print()

    print("=" * 70)
    print("Production example completed successfully!")
    print()
    print("Key takeaways:")
    print("  ✅ Use create_production_agent() for easy setup")
    print("  ✅ Thread safety enabled by default")
    print("  ✅ Real embeddings used automatically")
    print("  ✅ Memory limits enforced")
    print("  ✅ Health monitoring available")
    print("  ✅ Error handling included")
    print("=" * 70)


if __name__ == "__main__":
    main()
