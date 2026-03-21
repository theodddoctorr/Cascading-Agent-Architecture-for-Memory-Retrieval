"""
Multi-agent example demonstrating:
- Multiple agents with shared or separate memory
- Agent collaboration
- Specialized agents for different domains
"""

from cascading_agent import CascadingAgent, AgentConfig, TierConfig, RetrievalStrategy
import numpy as np


def create_domain_agent(domain_name: str, documents: list) -> CascadingAgent:
    """Create a specialized agent for a specific domain."""
    config = AgentConfig(
        tier_configs=[
            TierConfig(name=f"{domain_name}_fast", capacity=10, access_time_ms=1.0),
            TierConfig(name=f"{domain_name}_slow", capacity=100, access_time_ms=20.0)
        ],
        retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
        auto_promote=True
    )

    agent = CascadingAgent(config)

    # Add domain-specific documents
    for doc in documents:
        agent.add(content=doc, metadata={"domain": domain_name})

    return agent


def main():
    print("=" * 70)
    print("Multi-Agent Cascading Architecture Example")
    print("=" * 70)
    print()

    # Create specialized agents for different domains
    print("Creating specialized domain agents...")
    print()

    # Technical agent
    tech_docs = [
        "The cascading architecture uses multiple memory tiers",
        "Vector embeddings enable semantic search",
        "LRU eviction policy removes least recently used items",
        "Auto-promotion moves frequent items to faster tiers",
        "Query optimization reduces average latency"
    ]
    tech_agent = create_domain_agent("technical", tech_docs)
    print(f"  ✓ Technical Agent: {sum(t.size() for t in tech_agent.tiers)} docs")

    # Business agent
    business_docs = [
        "The system improves user experience through faster response times",
        "Cost optimization through tiered storage pricing",
        "Scalability enables handling millions of users",
        "Analytics provide insights into usage patterns",
        "ROI increases with improved performance metrics"
    ]
    business_agent = create_domain_agent("business", business_docs)
    print(f"  ✓ Business Agent: {sum(t.size() for t in business_agent.tiers)} docs")

    # Research agent
    research_docs = [
        "Memory hierarchies have been studied extensively in computer architecture",
        "Caching strategies impact overall system performance",
        "Recent papers explore ML-based promotion policies",
        "Benchmarks show 3x improvement in retrieval speed",
        "Future work includes adaptive tier sizing"
    ]
    research_agent = create_domain_agent("research", research_docs)
    print(f"  ✓ Research Agent: {sum(t.size() for t in research_agent.tiers)} docs")

    print()
    print("-" * 70)
    print()

    # Test queries across different agents
    queries = [
        ("How does caching improve performance?", "technical"),
        ("What is the business value of faster systems?", "business"),
        ("What research exists on memory hierarchies?", "research")
    ]

    agents = {
        "technical": tech_agent,
        "business": business_agent,
        "research": research_agent
    }

    print("Querying specialized agents:")
    print()

    for query, domain in queries:
        print(f"Query: '{query}'")
        print(f"Domain: {domain}")
        print()

        agent = agents[domain]
        results = agent.query(query, top_k=2, threshold=0.1)

        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['content']}")
            print(f"     Similarity: {result['similarity']:.3f}, Tier: {result['tier']}")

        print()

    print("-" * 70)
    print()

    # Multi-agent consultation
    print("Multi-Agent Consultation:")
    print()

    consultation_query = "performance optimization strategies"
    print(f"Query: '{consultation_query}'")
    print("Consulting all agents...")
    print()

    all_results = []
    for domain_name, agent in agents.items():
        results = agent.query(consultation_query, top_k=1, threshold=0.05)
        for result in results:
            result['source_agent'] = domain_name
            all_results.append(result)

    # Sort by similarity
    all_results.sort(key=lambda x: x['similarity'], reverse=True)

    print("Combined results from all agents:")
    for i, result in enumerate(all_results, 1):
        print(f"  {i}. [{result['source_agent'].upper()}] {result['content']}")
        print(f"     Similarity: {result['similarity']:.3f}")
    print()

    print("-" * 70)
    print()

    # Show statistics for each agent
    print("Agent Statistics:")
    print()

    for domain_name, agent in agents.items():
        stats = agent.get_stats()
        print(f"{domain_name.upper()} Agent:")
        print(f"  Total items: {stats['total_items']}")
        print(f"  Total queries: {stats['query_stats']['total_queries']}")
        print(f"  Avg latency: {stats['query_stats']['avg_latency_ms']:.2f}ms")
        print(f"  Promotions: {stats['query_stats']['promotions']}")
        print()

    print("=" * 70)
    print("Multi-agent example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
