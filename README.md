# Cascading Agent Architecture for Memory Retrieval

**Author:** Jason Faulkner (also published as The OddDocTorr, DocTorr Why)

## Overview

This repository contains a research paper proposing a novel cascading agent architecture for efficient memory retrieval in AI systems. The architecture addresses challenges in managing and retrieving information from large memory stores in agent-based systems.

## Contents

### Research Paper
- `Cascading Agent Architecture for Memory Retrieval.pdf` - Full research paper
- `CITATION.cff` - Citation information in Citation File Format
- `ATTRIBUTION.txt` - Attribution details

### Implementation
- `/implementations/python/` - **Reference Python implementation** (NEW!)
  - Complete working implementation of the architecture
  - Examples, tests, and benchmarks included
  - Ready to use in your projects

### Documentation
- `/docs/` - Implementation guides and architecture documentation
- `DEPENDENCY_AUDIT.md` - Dependency and security audit report
- `checksums_with_frontmatter.json` - File integrity checksums

## How to Cite

If you use or reference this work, please cite it as:

```bibtex
@article{faulkner2025cascading,
  title={Cascading Agent Architecture for Memory Retrieval},
  author={Faulkner, Jason},
  year={2025},
  note={Preprint}
}
```

For more citation formats, see `CITATION.cff`.

## Quick Start

### Using the Python Implementation

```bash
# Install
cd implementations/python
pip install -e .

# Run examples
python examples/basic_usage.py
python examples/advanced_retrieval.py

# Run tests
pytest tests/

# Run benchmarks
python benchmarks/performance_test.py
```

### Basic Usage

```python
from cascading_agent import CascadingAgent, AgentConfig, TierConfig

# Configure memory tiers
tier_configs = [
    TierConfig(name="fast", capacity=100, access_time_ms=1.0),
    TierConfig(name="slow", capacity=1000, access_time_ms=50.0)
]

# Create agent
config = AgentConfig(tier_configs=tier_configs)
agent = CascadingAgent(config)

# Add content
agent.add("The cascading architecture provides efficient retrieval")

# Query
results = agent.query("efficient retrieval", top_k=5)
for result in results:
    print(f"{result['content']} (similarity: {result['similarity']:.2f})")
```

See `/implementations/python/README.md` and `/docs/IMPLEMENTATION_GUIDE.md` for detailed documentation.

## Licensing

- **Text, figures, and PDF:** [CC BY 4.0](LICENSE) - You are free to share and adapt with attribution
- **Source code (if any):** [Apache-2.0](LICENSE-CODE)

## File Integrity

Checksums for verifying file integrity are provided in `checksums_with_frontmatter.json`. To verify:

```bash
sha256sum "Cascading Agent Architecture for Memory Retrieval.pdf"
# Compare with: 5a44dde1a86a40f74267aa5e84800616dadb711afb363257470e4e3924fe5662
```

## Contributing

This is currently a documentation repository. If you would like to:
- Report issues or suggest improvements to the paper
- Contribute reference implementations
- Discuss the architecture

Please open an issue or contact the author.

## Version

Current version: 1.0.0 (Released: 2025-09-30)

See `CHANGELOG.md` for version history.
