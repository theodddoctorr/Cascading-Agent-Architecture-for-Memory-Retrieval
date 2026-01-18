# Implementation Guide

Complete guide to implementing the Cascading Agent Architecture for Memory Retrieval.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Advanced Topics](#advanced-topics)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

The Cascading Agent Architecture provides an efficient multi-tier memory system for AI agents, optimizing the trade-off between access speed and storage capacity.

### Key Benefits

- **Fast Access**: Frequently accessed items in fast tiers (1-10ms)
- **Large Capacity**: Infrequently accessed items in slower, larger tiers (50-100ms)
- **Automatic Optimization**: Items automatically promoted based on access patterns
- **Scalability**: Handles millions of items efficiently

### Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              Cascading Agent                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  Query ──→ Cascading Retrieval Engine           │
│                      │                           │
│                      ├──→ Tier 1 (Fast)         │
│                      │    Capacity: 10-100       │
│                      │    Latency: 1-5ms         │
│                      │                           │
│                      ├──→ Tier 2 (Medium)       │
│                      │    Capacity: 100-1000     │
│                      │    Latency: 10-20ms       │
│                      │                           │
│                      └──→ Tier 3 (Slow)         │
│                           Capacity: 1000+        │
│                           Latency: 50-100ms      │
│                                                  │
│  Auto-Promotion: Hot items → Faster tiers       │
│  Eviction: Cold items → Slower tiers/removed    │
└─────────────────────────────────────────────────┘
```

## Core Concepts

### 1. Memory Tiers

Each tier has:
- **Capacity**: Maximum number of items
- **Access Time**: Latency for retrieval
- **Eviction Policy**: How to handle capacity overflow (LRU, LFU, FIFO)
- **Promotion Threshold**: Score needed for promotion to faster tier

### 2. Retrieval Strategies

#### Sequential
```python
# Try tiers in order, stop when results found
for tier in tiers:
    results = tier.search(query)
    if len(results) >= top_k:
        return results
```

**Pros**: Low latency when hits fast tiers
**Cons**: Worst-case latency equals slowest tier
**Best for**: Queries with predictable access patterns

#### Parallel
```python
# Query all tiers simultaneously
results = parallel_map(lambda tier: tier.search(query), tiers)
merged = merge_and_deduplicate(results)
return top_k(merged)
```

**Pros**: Consistent latency
**Cons**: Always pays cost of slowest tier
**Best for**: Unpredictable queries, need guaranteed latency

#### Adaptive
```python
# Choose strategy based on query characteristics
if query.is_specific():  # High threshold
    return parallel_retrieve()
else:  # Broad query
    return sequential_retrieve()
```

**Pros**: Best of both worlds
**Cons**: Requires query analysis
**Best for**: Mixed workloads

### 3. Auto-Promotion

Items are promoted when:
- Access frequency exceeds threshold
- Recent access pattern (time-based decay)
- Combined score: `0.6 * recency + 0.4 * frequency`

```python
def should_promote(item):
    recency_score = exp_decay(time_since_access, half_life=1h)
    frequency_score = min(access_count / 10.0, 1.0)
    score = 0.6 * recency_score + 0.4 * frequency_score
    return score >= promotion_threshold
```

### 4. Eviction Policies

#### LRU (Least Recently Used)
- Evict item not accessed longest
- Best for: Temporal locality
- Implementation: OrderedDict

#### LFU (Least Frequently Used)
- Evict item with lowest access count
- Best for: Clear hot/cold patterns
- Implementation: Access counter + min-heap

#### FIFO (First In, First Out)
- Evict oldest item
- Best for: Streaming data
- Implementation: Queue

## Step-by-Step Implementation

### Step 1: Basic Setup

```python
from cascading_agent import CascadingAgent, AgentConfig, TierConfig

# Define tiers (fast to slow)
tier_configs = [
    TierConfig(
        name="L1_cache",
        capacity=50,
        access_time_ms=1.0,
        eviction_policy="lru"
    ),
    TierConfig(
        name="L2_storage",
        capacity=500,
        access_time_ms=20.0,
        eviction_policy="lfu"
    )
]

# Create agent
config = AgentConfig(tier_configs=tier_configs)
agent = CascadingAgent(config)
```

### Step 2: Adding Content

```python
# Simple add
agent.add("Python is a programming language")

# With metadata
agent.add(
    "Machine learning uses neural networks",
    metadata={"category": "ML", "difficulty": "intermediate"}
)

# With custom ID
agent.add(
    "Databases store structured data",
    item_id="db_intro_001"
)

# With precomputed embedding
import numpy as np
embedding = your_embedding_model.encode("Custom text")
agent.add("Custom text", embedding=embedding)
```

### Step 3: Querying

```python
# Basic query
results = agent.query("What is Python?")

# With parameters
results = agent.query(
    query="machine learning",
    top_k=10,           # Return top 10 results
    threshold=0.7,      # Minimum similarity 70%
    max_tiers=2         # Search only first 2 tiers
)

# Process results
for result in results:
    print(f"Content: {result['content']}")
    print(f"Similarity: {result['similarity']:.2%}")
    print(f"From tier: {result['tier']}")
    print(f"Accessed: {result['access_count']} times")
```

### Step 4: Using Custom Embeddings

```python
# Option 1: Sentence Transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed(text):
    return model.encode(text)

config = AgentConfig(
    tier_configs=tier_configs,
    embedding_function=embed
)
agent = CascadingAgent(config)
```

```python
# Option 2: OpenAI
from openai import OpenAI
import numpy as np

client = OpenAI(api_key="your-key")

def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)

config = AgentConfig(
    tier_configs=tier_configs,
    embedding_function=embed
)
```

### Step 5: Monitoring and Optimization

```python
# Get statistics
stats = agent.get_stats()

print(f"Total queries: {stats['query_stats']['total_queries']}")
print(f"Avg latency: {stats['query_stats']['avg_latency_ms']:.2f}ms")
print(f"Promotions: {stats['query_stats']['promotions']}")

# Per-tier stats
for tier_stat in stats['tier_stats']:
    print(f"{tier_stat['name']}:")
    print(f"  Size: {tier_stat['size']}/{tier_stat['capacity']}")
    print(f"  Hit rate: {tier_stat['hit_rate']:.2%}")
    print(f"  Evictions: {tier_stat['evictions']}")
```

## Advanced Topics

### Multi-Agent Systems

```python
# Create specialized agents
tech_agent = CascadingAgent(tech_config)
business_agent = CascadingAgent(business_config)

# Add domain-specific content
tech_agent.add("Technical documentation...")
business_agent.add("Business reports...")

# Query appropriate agent
if query_is_technical(query):
    results = tech_agent.query(query)
else:
    results = business_agent.query(query)

# Or combine results
tech_results = tech_agent.query(query, top_k=3)
biz_results = business_agent.query(query, top_k=3)
combined = merge_results(tech_results, biz_results)
```

### Memory Persistence

```python
# Export memory
exported = agent.export_memory()

# Save to file
import json
with open('memory_snapshot.json', 'w') as f:
    json.dump(exported, f)

# Load and import
with open('memory_snapshot.json', 'r') as f:
    data = json.load(f)

new_agent = CascadingAgent(config)
new_agent.import_memory(data)
```

### Dynamic Tier Resizing

```python
# Monitor utilization
tier_info = agent.get_tier_info()

for info in tier_info:
    if info['utilization'] > 0.9:
        print(f"Tier {info['name']} is 90% full - consider resizing")

# Note: Current implementation requires recreating agent
# for tier resizing. In production, implement dynamic resizing.
```

### Custom Eviction Policies

```python
# Extend MemoryTier to add custom eviction
from cascading_agent.memory_tier import MemoryTier

class CustomMemoryTier(MemoryTier):
    def _evict_one(self):
        # Custom logic: evict based on custom score
        item_id = min(
            self.items.keys(),
            key=lambda k: self._custom_score(self.items[k])
        )
        return self.items.pop(item_id)

    def _custom_score(self, item):
        # Lower score = more likely to evict
        age = time.time() - item.creation_time
        size = len(item.content)
        return item.access_count / (age * size)
```

## Best Practices

### 1. Tier Configuration

**DO:**
- Use 2-4 tiers (diminishing returns beyond 4)
- Make tier capacities grow geometrically (10, 100, 1000)
- Set access times realistically based on your storage backend

**DON'T:**
- Create too many tiers (overhead increases)
- Make tiers equal size (defeats purpose)
- Ignore actual latency characteristics

### 2. Embedding Selection

**DO:**
- Use domain-specific embeddings when possible
- Cache embeddings for reused content
- Normalize vectors for cosine similarity

**DON'T:**
- Use random/hash embeddings in production
- Mix different embedding models
- Forget to handle embedding dimension changes

### 3. Query Optimization

**DO:**
- Set appropriate similarity thresholds (0.7-0.8 typical)
- Limit top_k to what you actually need
- Use max_tiers to bound latency

**DON'T:**
- Request hundreds of results (degrades performance)
- Set threshold too low (returns irrelevant items)
- Always query all tiers if first tier suffices

### 4. Monitoring

**DO:**
- Monitor hit rates per tier
- Track promotion effectiveness
- Watch for skewed access patterns

**DON'T:**
- Ignore degrading hit rates
- Let tiers become unbalanced
- Forget to analyze slow queries

## Troubleshooting

### Low Hit Rate on Fast Tiers

**Symptoms**: Most queries hit slow tiers

**Causes**:
- Promotion threshold too high
- Fast tier too small
- Access pattern too random

**Solutions**:
```python
# Lower promotion threshold
TierConfig(promotion_threshold=0.3)  # instead of 0.5

# Increase fast tier capacity
TierConfig(capacity=200)  # instead of 50

# Check access patterns
stats = agent.get_stats()
print(stats['tier_stats'])
```

### High Latency

**Symptoms**: Queries taking too long

**Causes**:
- Always hitting slow tiers
- Too many items per tier
- Inefficient retrieval strategy

**Solutions**:
```python
# Use parallel strategy
config = AgentConfig(
    tier_configs=tier_configs,
    retrieval_strategy=RetrievalStrategy.PARALLEL
)

# Limit search depth
results = agent.query(query, max_tiers=2)

# Enable auto-promotion
config = AgentConfig(
    tier_configs=tier_configs,
    auto_promote=True
)
```

### Memory Bloat

**Symptoms**: Too many items in tiers

**Causes**:
- Eviction not working
- Tiers too large
- Adding duplicates

**Solutions**:
```python
# Check for duplicates
exported = agent.export_memory()
ids = [item['item_id'] for item in exported]
if len(ids) != len(set(ids)):
    print("Duplicates found!")

# Reduce tier sizes
TierConfig(capacity=100)  # instead of 1000

# More aggressive eviction
TierConfig(eviction_policy="fifo")  # instead of lfu
```

### Poor Relevance

**Symptoms**: Retrieved items don't match query

**Causes**:
- Embedding quality issues
- Threshold too low
- Metadata not used

**Solutions**:
```python
# Use better embeddings
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-mpnet-base-v2')

# Increase threshold
results = agent.query(query, threshold=0.8)

# Post-filter by metadata
results = [r for r in results if r['metadata'].get('category') == 'relevant']
```

## Next Steps

1. **Read API Reference**: See [API_REFERENCE.md](API_REFERENCE.md)
2. **Study Examples**: Check `/implementations/python/examples/`
3. **Run Benchmarks**: Test performance for your use case
4. **Integrate**: Add to your agent system
5. **Optimize**: Tune based on your access patterns

## Additional Resources

- Research Paper: See repository root for full theoretical background
- Example Code: `/implementations/python/examples/`
- Tests: `/implementations/python/tests/` for usage examples
- Benchmarks: `/implementations/python/benchmarks/` for performance testing
