"""
Performance benchmarks for the Cascading Agent Architecture.

Tests various scenarios and configurations to measure:
- Query latency
- Throughput
- Memory efficiency
- Promotion effectiveness
"""

import time
import numpy as np
from cascading_agent import (
    CascadingAgent,
    AgentConfig,
    TierConfig,
    RetrievalStrategy
)


def benchmark_query_latency(num_items: int = 1000, num_queries: int = 100):
    """Benchmark query latency with different configurations."""
    print("\n" + "=" * 70)
    print(f"Query Latency Benchmark ({num_items} items, {num_queries} queries)")
    print("=" * 70)

    configurations = [
        ("2-Tier Sequential", [
            TierConfig(name="fast", capacity=100, access_time_ms=1.0),
            TierConfig(name="slow", capacity=num_items, access_time_ms=50.0)
        ], RetrievalStrategy.SEQUENTIAL),

        ("3-Tier Sequential", [
            TierConfig(name="L1", capacity=50, access_time_ms=1.0),
            TierConfig(name="L2", capacity=200, access_time_ms=10.0),
            TierConfig(name="L3", capacity=num_items, access_time_ms=50.0)
        ], RetrievalStrategy.SEQUENTIAL),

        ("3-Tier Parallel", [
            TierConfig(name="L1", capacity=50, access_time_ms=1.0),
            TierConfig(name="L2", capacity=200, access_time_ms=10.0),
            TierConfig(name="L3", capacity=num_items, access_time_ms=50.0)
        ], RetrievalStrategy.PARALLEL),
    ]

    results = {}

    for config_name, tier_configs, strategy in configurations:
        print(f"\nTesting: {config_name}")

        # Create agent
        config = AgentConfig(
            tier_configs=tier_configs,
            retrieval_strategy=strategy,
            auto_promote=True
        )
        agent = CascadingAgent(config)

        # Add items
        print(f"  Adding {num_items} items...")
        for i in range(num_items):
            agent.add(f"Document {i} with various content about topic {i % 10}")

        # Run queries
        print(f"  Running {num_queries} queries...")
        query_times = []

        for i in range(num_queries):
            query = f"topic {i % 10}"
            start = time.time()
            agent.query(query, top_k=5)
            elapsed = (time.time() - start) * 1000  # ms
            query_times.append(elapsed)

        # Calculate statistics
        avg_latency = np.mean(query_times)
        median_latency = np.median(query_times)
        p95_latency = np.percentile(query_times, 95)
        p99_latency = np.percentile(query_times, 99)

        results[config_name] = {
            "avg": avg_latency,
            "median": median_latency,
            "p95": p95_latency,
            "p99": p99_latency
        }

        print(f"    Avg: {avg_latency:.2f}ms")
        print(f"    Median: {median_latency:.2f}ms")
        print(f"    P95: {p95_latency:.2f}ms")
        print(f"    P99: {p99_latency:.2f}ms")

    # Summary
    print("\n" + "-" * 70)
    print("Summary:")
    for name, metrics in results.items():
        print(f"  {name:25s}: avg={metrics['avg']:6.2f}ms, "
              f"p95={metrics['p95']:6.2f}ms")

    return results


def benchmark_throughput(duration_seconds: int = 5):
    """Benchmark query throughput (queries per second)."""
    print("\n" + "=" * 70)
    print(f"Throughput Benchmark ({duration_seconds}s)")
    print("=" * 70)

    config = AgentConfig(
        tier_configs=[
            TierConfig(name="fast", capacity=100, access_time_ms=1.0),
            TierConfig(name="slow", capacity=1000, access_time_ms=10.0)
        ],
        retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
        auto_promote=True
    )
    agent = CascadingAgent(config)

    # Add data
    print("  Adding 500 items...")
    for i in range(500):
        agent.add(f"Document {i}")

    # Run queries for fixed duration
    print(f"  Running queries for {duration_seconds} seconds...")
    start_time = time.time()
    query_count = 0

    while time.time() - start_time < duration_seconds:
        agent.query("test query", top_k=5)
        query_count += 1

    elapsed = time.time() - start_time
    qps = query_count / elapsed

    print(f"\n  Results:")
    print(f"    Total queries: {query_count}")
    print(f"    Duration: {elapsed:.2f}s")
    print(f"    Throughput: {qps:.2f} queries/second")

    return qps


def benchmark_memory_efficiency():
    """Benchmark memory efficiency with different tier configurations."""
    print("\n" + "=" * 70)
    print("Memory Efficiency Benchmark")
    print("=" * 70)

    configurations = [
        ("No tiers (single)", [
            TierConfig(name="single", capacity=1000)
        ]),
        ("2 tiers", [
            TierConfig(name="fast", capacity=100),
            TierConfig(name="slow", capacity=1000)
        ]),
        ("3 tiers", [
            TierConfig(name="L1", capacity=50),
            TierConfig(name="L2", capacity=200),
            TierConfig(name="L3", capacity=1000)
        ]),
    ]

    for config_name, tier_configs in configurations:
        print(f"\n  Testing: {config_name}")

        config = AgentConfig(
            tier_configs=tier_configs,
            auto_promote=True
        )
        agent = CascadingAgent(config)

        # Add 500 items
        for i in range(500):
            agent.add(f"Item {i}")

        # Query with zipf distribution (some items accessed more)
        for _ in range(200):
            # Most queries for first 50 items
            item_id = int(np.random.zipf(1.5) % 50)
            agent.query(f"Item {item_id}")

        # Check tier distribution
        tier_info = agent.get_tier_info()
        stats = agent.get_stats()

        print(f"    Tier distribution:")
        for info in tier_info:
            print(f"      {info['name']:10s}: {info['size']:3d}/{info['capacity']:4d} "
                  f"({info['utilization']:5.1%}), hits={info['hits']}")

        print(f"    Promotions: {stats['query_stats']['promotions']}")
        print(f"    Avg latency: {stats['query_stats']['avg_latency_ms']:.2f}ms")


def benchmark_promotion_effectiveness():
    """Benchmark effectiveness of auto-promotion."""
    print("\n" + "=" * 70)
    print("Auto-Promotion Effectiveness Benchmark")
    print("=" * 70)

    # Test with and without auto-promotion
    for auto_promote in [False, True]:
        print(f"\n  Auto-promote: {auto_promote}")

        config = AgentConfig(
            tier_configs=[
                TierConfig(name="fast", capacity=20, access_time_ms=1.0),
                TierConfig(name="slow", capacity=200, access_time_ms=50.0)
            ],
            retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
            auto_promote=auto_promote
        )
        agent = CascadingAgent(config)

        # Add 100 items
        for i in range(100):
            agent.add(f"Document {i}")

        # Query hot items repeatedly
        hot_items = [0, 1, 2, 3, 4]  # First 5 items are "hot"

        query_times = []
        for _ in range(50):
            for item_id in hot_items:
                start = time.time()
                agent.query(f"Document {item_id}")
                elapsed = (time.time() - start) * 1000
                query_times.append(elapsed)

        stats = agent.get_stats()
        tier_info = agent.get_tier_info()

        print(f"    Avg query time: {np.mean(query_times):.2f}ms")
        print(f"    Promotions: {stats['query_stats']['promotions']}")
        print(f"    Fast tier utilization: {tier_info[0]['utilization']:.1%}")


def benchmark_scaling():
    """Benchmark how performance scales with data size."""
    print("\n" + "=" * 70)
    print("Scaling Benchmark")
    print("=" * 70)

    data_sizes = [100, 500, 1000, 5000]

    config_template = AgentConfig(
        tier_configs=[
            TierConfig(name="fast", capacity=100, access_time_ms=1.0),
            TierConfig(name="slow", capacity=10000, access_time_ms=10.0)
        ],
        retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
        auto_promote=True
    )

    for size in data_sizes:
        print(f"\n  Dataset size: {size} items")

        agent = CascadingAgent(config_template)

        # Add data
        add_start = time.time()
        for i in range(size):
            agent.add(f"Document {i} with content")
        add_time = (time.time() - add_start) * 1000

        # Query
        query_times = []
        for i in range(20):
            start = time.time()
            agent.query(f"Document {i}")
            query_times.append((time.time() - start) * 1000)

        print(f"    Add time: {add_time:.2f}ms ({add_time/size:.3f}ms per item)")
        print(f"    Avg query time: {np.mean(query_times):.2f}ms")


def main():
    """Run all benchmarks."""
    print("\n" + "=" * 70)
    print("Cascading Agent Architecture - Performance Benchmarks")
    print("=" * 70)

    benchmark_query_latency(num_items=1000, num_queries=100)
    benchmark_throughput(duration_seconds=3)
    benchmark_memory_efficiency()
    benchmark_promotion_effectiveness()
    benchmark_scaling()

    print("\n" + "=" * 70)
    print("All benchmarks completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
