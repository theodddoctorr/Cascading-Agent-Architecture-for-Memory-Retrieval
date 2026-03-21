# Cascading Agent Architecture - Python Implementation

A reference implementation of the Cascading Agent Architecture for Memory Retrieval in Python.

## Features

- **Multi-Tier Memory System**: Configurable memory tiers with different capacities and access speeds
- **Intelligent Retrieval**: Sequential, parallel, and adaptive retrieval strategies
- **Auto-Promotion**: Frequently accessed items automatically promoted to faster tiers
- **Flexible Eviction**: LRU, LFU, and FIFO eviction policies
- **Semantic Search**: Vector embedding-based similarity search
- **Performance Optimized**: Efficient memory management and query optimization

## Installation

### From Source

```bash
cd implementations/python
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

### With Enhanced Embeddings

```bash
pip install -e ".[embeddings]"
```

## Quick Start

```python
from cascading_agent import CascadingAgent, AgentConfig, TierConfig

# Configure memory tiers
tier_configs = [
    TierConfig(name="fast_cache", capacity=100, access_time_ms=1.0),
    TierConfig(name="slow_storage", capacity=1000, access_time_ms=50.0)
]

# Create agent
config = AgentConfig(tier_configs=tier_configs)
agent = CascadingAgent(config)

# Add content
agent.add("The cascading architecture provides efficient retrieval")
agent.add("Memory tiers optimize for speed and capacity")

# Query
results = agent.query("efficient retrieval systems", top_k=5)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Similarity: {result['similarity']:.3f}")
    print(f"Tier: {result['tier']}")
```

## Examples

### Basic Usage

```bash
python examples/basic_usage.py
```

### Advanced Retrieval

```bash
python examples/advanced_retrieval.py
```

### Multi-Agent Systems

```bash
python examples/multi_agent.py
```

## Running Tests

```bash
# Run all tests
pytest tests/

# With coverage
pytest tests/ --cov=cascading_agent --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

## Benchmarks

```bash
python benchmarks/performance_test.py
```

## Architecture

### Core Components

1. **MemoryTier**: Individual memory tier with configurable capacity and eviction policy
2. **CascadingRetrieval**: Orchestrates search across multiple tiers
3. **CascadingAgent**: High-level API for agent interaction

### Retrieval Strategies

- **Sequential**: Try each tier in order until results found (low latency for hits)
- **Parallel**: Query all tiers simultaneously (consistent latency)
- **Adaptive**: Choose strategy based on query characteristics

### Eviction Policies

- **LRU** (Least Recently Used): Evict items not accessed recently
- **LFU** (Least Frequently Used): Evict items accessed least often
- **FIFO** (First In, First Out): Evict oldest items

## Configuration

### Tier Configuration

```python
TierConfig(
    name="my_tier",
    capacity=1000,              # Maximum items in tier
    access_time_ms=10.0,        # Simulated access latency
    eviction_policy="lru",      # Eviction policy (lru, lfu, fifo)
    promotion_threshold=0.5,    # Score threshold for promotion
    decay_half_life=3600.0      # Time-based relevance decay (seconds)
)
```

### Agent Configuration

```python
AgentConfig(
    tier_configs=[...],                        # List of TierConfig objects
    retrieval_strategy=RetrievalStrategy.SEQUENTIAL,
    auto_promote=True,                         # Enable auto-promotion
    embedding_function=custom_func,            # Custom embedding function
    default_top_k=5,                          # Default number of results
    default_threshold=0.7                      # Default similarity threshold
)
```

## Custom Embeddings

By default, the implementation uses a simple hash-based embedding for demonstration.
For production use, integrate with proper embedding models:

### Using Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str):
    return model.encode(text)

config = AgentConfig(
    tier_configs=[...],
    embedding_function=embed_text
)
```

### Using OpenAI

```python
from openai import OpenAI

client = OpenAI()

def embed_text(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)

config = AgentConfig(
    tier_configs=[...],
    embedding_function=embed_text
)
```

## Performance

Typical performance characteristics (benchmarked on modern CPU):

- **Query Latency**: 1-50ms depending on tier hit
- **Throughput**: 100-1000 queries/second
- **Memory Efficiency**: 70-90% utilization with auto-promotion

See `benchmarks/performance_test.py` for detailed benchmarks.

## API Reference

### CascadingAgent

- `add(content, metadata=None, embedding=None, item_id=None)`: Add content to memory
- `query(query, top_k=5, threshold=0.7, max_tiers=None)`: Query the memory system
- `chat(message, context_k=3, threshold=0.7)`: Chat interface with context retrieval
- `get_stats()`: Get comprehensive statistics
- `clear_memory()`: Clear all memory tiers
- `export_memory()`: Export memory items
- `import_memory(items)`: Import memory items

### MemoryTier

- `add(item_id, item)`: Add item to tier
- `get(item_id)`: Retrieve item by ID
- `search(query_embedding, top_k, threshold)`: Semantic search
- `get_stats()`: Get tier statistics

### CascadingRetrieval

- `retrieve(query_embedding, top_k, threshold, max_tiers)`: Perform cascading retrieval
- `add_item(item_id, content, embedding, metadata, target_tier)`: Add item to system
- `get_stats()`: Get retrieval statistics

## Contributing

See the main repository [CONTRIBUTING.md](../../.github/CONTRIBUTING.md) for guidelines.

## License

Apache-2.0 - See [LICENSE-CODE](../../LICENSE-CODE) for details.

## Citation

If you use this implementation in your research, please cite:

```bibtex
@software{faulkner2025cascading_impl,
  author = {Faulkner, Jason},
  title = {Cascading Agent Architecture for Memory Retrieval - Python Implementation},
  year = {2025},
  url = {https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval}
}
```

## Related Work

- Research Paper: See `Cascading Agent Architecture for Memory Retrieval.pdf` in repository root
- Documentation: See `/docs` directory for detailed guides

## Support

- Issues: [GitHub Issues](https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval/issues)
- Discussions: [GitHub Discussions](https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval/discussions)
