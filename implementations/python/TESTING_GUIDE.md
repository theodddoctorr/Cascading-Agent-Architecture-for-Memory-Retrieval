# Testing Guide

Ready to test the Cascading Agent Architecture with your own files!

## Quick Status Check

### ✅ What's Working

1. **Core Implementation** - All modules functional
   - Memory tiers (fast/medium/slow)
   - Cascading retrieval strategies
   - Agent API
   - Production hardening

2. **Production Features** - All 3 critical issues fixed
   - Thread safety (threading.RLock)
   - Memory limits (max_items enforcement)
   - Embedding auto-detection (sentence-transformers)

3. **Testing Tools** - Ready to use
   - Quick test script (`quick_test.py`)
   - File loader example (`examples/file_loader.py`)
   - Production example (`examples/production_ready.py`)

### ⚠️ Current Limitations

1. **Default Embeddings** - Hash-based (NOT production quality)
   - Works for exact/near-exact matches only
   - Does NOT work well for semantic similarity
   - **Fix**: Install sentence-transformers (see below)

2. **Dependencies** - Minimal installation
   - Only numpy installed (core requirement)
   - sentence-transformers recommended for production
   - pytest needed for running test suite

## Quick Start - Test Installation

```bash
cd /home/user/Cascading-Agent-Architecture-for-Memory-Retrieval/implementations/python

# 1. Verify everything works
python3 quick_test.py
```

**Expected output**: All 7 tests should pass with green checkmarks ✓

## Test With Your Files

### Basic File Loading

```bash
# Load a single file
python3 examples/file_loader.py /path/to/your/file.txt

# Load multiple files
python3 examples/file_loader.py file1.txt file2.md file3.py

# Load entire directory (recursively)
python3 examples/file_loader.py /path/to/directory
```

### Interactive Mode (Recommended!)

```bash
# Load files and start interactive query mode
python3 examples/file_loader.py /path/to/files --interactive

# Then type queries:
Query: What is the main purpose of this code?
Query: How does error handling work?
Query: quit  # to exit
```

### Advanced Options

```bash
# Customize chunk size (default: 500 words)
python3 examples/file_loader.py docs/ --chunk-size 300

# Change number of results (default: 5)
python3 examples/file_loader.py docs/ --top-k 10 --interactive

# Load and test
python3 examples/file_loader.py README.md CHANGELOG.md docs/ --interactive
```

## Improve Results - Install Better Embeddings

The default hash-based embeddings are **NOT suitable for semantic search**. For production-quality results:

```bash
# Install sentence-transformers
pip3 install sentence-transformers

# Now test again - much better results!
python3 examples/file_loader.py /path/to/files --interactive
```

**What changes**:
- Semantic similarity search works properly
- "programming language" matches "Python" and "code"
- Understands context and meaning
- Much more accurate retrieval

## Test Production Features

```bash
# Run production example
python3 examples/production_ready.py
```

This demonstrates:
- ProductionAgent with all fixes
- Health monitoring
- Thread safety
- Memory limits
- Error handling
- Logging

## Run Full Test Suite (Optional)

```bash
# Install pytest
pip3 install pytest

# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py -v

# Run benchmarks
python3 benchmarks/performance_test.py
```

## Supported File Types

The file loader supports common text formats:
- `.txt` - Plain text
- `.md` - Markdown
- `.py` - Python
- `.js` - JavaScript
- `.java` - Java
- `.c`, `.cpp`, `.h` - C/C++
- `.rs` - Rust
- `.go` - Go
- `.rb` - Ruby
- `.sh` - Shell scripts
- `.yaml`, `.yml` - YAML
- `.json` - JSON
- `.xml` - XML
- `.html`, `.css` - Web
- `.rst` - reStructuredText

To add more formats, edit `file_loader.py` line 83 (`extensions` tuple).

## Custom Usage - Your Own Script

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cascading_agent import create_production_agent

# Create agent
agent = create_production_agent(
    tier_capacities=[50, 500, 5000],    # Fast, medium, slow tiers
    max_items=50000,                     # Total capacity
    enable_thread_safety=True,           # Safe for concurrent use
    log_level="INFO"                     # Logging verbosity
)

# Add your content
agent.add("Your document content here", item_id="doc1")
agent.add("More content", metadata={"source": "file.txt"})

# Query
results = agent.query("your search query", top_k=5)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Metadata: {result.get('metadata', {})}")
    print()

# Check health
health = agent.get_health_status()
print(f"Status: {health['status']}")
print(f"Capacity: {health['capacity_used']:.1%}")
```

## What Files Do You Have?

Tell me about your files and I can help you:
1. Test the implementation with your specific files
2. Customize the file loader for your needs
3. Create a custom script for your use case
4. Optimize settings for your data

**Next steps**:
- Try `python3 quick_test.py` to verify installation
- Try `python3 examples/file_loader.py /path/to/your/files --interactive`
- Install sentence-transformers for better results
- Let me know what you'd like to test!
