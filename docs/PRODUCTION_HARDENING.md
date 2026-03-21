# Production Hardening Guide

Complete guide to making the Cascading Agent Architecture production-ready by fixing the top 3 critical issues.

## Table of Contents

1. [Quick Start - Use ProductionAgent](#quick-start)
2. [Problem #1: Poor Embeddings](#problem-1-poor-embeddings)
3. [Problem #2: Memory Limits](#problem-2-memory-limits)
4. [Problem #3: Thread Safety](#problem-3-thread-safety)
5. [Additional Hardening](#additional-hardening)
6. [Production Checklist](#production-checklist)

---

## Quick Start

**The easiest way: Use `ProductionAgent`**

```python
from cascading_agent import create_production_agent

# One line to create a production-ready agent
agent = create_production_agent(
    tier_capacities=[50, 500, 5000],
    max_items=10000,
    enable_thread_safety=True,
    log_level="INFO"
)

# Use normally
agent.add("Some content")
results = agent.query("query text")

# Check health
health = agent.get_health_status()
print(f"Status: {health['status']}, Capacity: {health['capacity_used']:.1%}")
```

**What you get automatically:**
- ✅ Real embeddings (sentence-transformers if installed, fallback otherwise)
- ✅ Thread safety with locks
- ✅ Memory limit enforcement
- ✅ Capacity monitoring
- ✅ Error handling and logging
- ✅ Health status checks

---

## Problem #1: Poor Embeddings

### **Issue**
Default embedding is hash-based (demo only), causing poor semantic similarity.

**Severity:** 🔴 CRITICAL (85% probability of hitting this)

### **Symptoms**
- Queries don't find relevant items
- Similarity scores don't correlate with actual meaning
- Everything seems equally similar
- Results appear random

### **Solution 1: Use Sentence Transformers (Recommended)**

```python
# Install
pip install sentence-transformers

# Use in your code
from sentence_transformers import SentenceTransformer
from cascading_agent import CascadingAgent, AgentConfig, TierConfig

# Load model (do this once, not per query)
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality

# Create embedding function
def embed_text(text: str):
    return model.encode(text, show_progress_bar=False)

# Use in agent config
config = AgentConfig(
    tier_configs=[...],
    embedding_function=embed_text
)

agent = CascadingAgent(config)
```

**Available Models:**

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| `all-MiniLM-L6-v2` | 384 | Fast | Good | General purpose, production |
| `all-mpnet-base-v2` | 768 | Medium | Better | Higher quality needs |
| `all-distilroberta-v1` | 768 | Medium | Good | Balanced |

### **Solution 2: Use OpenAI Embeddings**

```python
# Install
pip install openai

# Use OpenAI
from openai import OpenAI
import numpy as np

client = OpenAI(api_key="your-api-key")

def embed_text(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",  # Or text-embedding-3-large
        input=text
    )
    return np.array(response.data[0].embedding)

config = AgentConfig(
    tier_configs=[...],
    embedding_function=embed_text
)
```

**Cost considerations:**
- OpenAI: ~$0.02 per 1M tokens
- Sentence Transformers: Free (runs locally)

### **Solution 3: Use ProductionAgent (Automatic)**

```python
from cascading_agent import create_production_agent

# Automatically tries to use sentence-transformers
# Falls back to improved hash-based if not available
agent = create_production_agent()
```

### **Validation**

Test your embeddings:

```python
# Add some content
agent.add("Python is a programming language")
agent.add("Java is used for enterprise applications")
agent.add("The quick brown fox jumps")

# Query
results = agent.query("programming languages", top_k=3)

# Check results
for r in results:
    print(f"{r['similarity']:.3f}: {r['content']}")

# Expected: Python and Java should rank higher than fox
# If fox ranks equally or higher, embeddings aren't working
```

---

## Problem #2: Memory Limits

### **Issue**
All data in RAM with no disk persistence, leading to OOM crashes.

**Severity:** 🟡 MEDIUM (60% probability)

### **Symptoms**
- Process killed by out-of-memory
- Slow performance with large datasets
- System swapping/thrashing

### **Limits**
- ~10K items: ✅ Fine
- ~50K items: ⚠️ Usable but slow
- ~100K+ items: ❌ Will crash

### **Solution 1: Set Reasonable Capacities**

```python
from cascading_agent import TierConfig

# DON'T do this (too large)
bad_config = [
    TierConfig(name="L1", capacity=10000),    # ❌ Too big
    TierConfig(name="L2", capacity=50000),    # ❌ Way too big
    TierConfig(name="L3", capacity=1000000)   # ❌ Will crash
]

# DO this (safe limits)
good_config = [
    TierConfig(name="L1", capacity=50),       # ✅ Small fast tier
    TierConfig(name="L2", capacity=500),      # ✅ Medium tier
    TierConfig(name="L3", capacity=5000)      # ✅ Large but safe
]
# Total: 5,550 items (safe)
```

**Rule of thumb:** Keep total capacity under 10,000 items.

### **Solution 2: Monitor Memory Usage**

```python
from cascading_agent import ProductionAgent

agent = ProductionAgent(
    config=config,
    max_items=10000  # Hard limit
)

# Check before adding
stats = agent.get_stats()
if stats['total_items'] > 9000:
    print("WARNING: Approaching capacity")
    # Trigger cleanup, stop adding, or alert

# Use health checks
health = agent.get_health_status()
if health['status'] in ['WARNING', 'CRITICAL']:
    print(f"Health issue: {health['status']}")
    print(f"Capacity: {health['capacity_used']:.1%}")
```

### **Solution 3: Implement Eviction Strategy**

```python
def add_with_eviction(agent, content, metadata=None):
    """Add content, evicting oldest if at capacity."""
    stats = agent.get_stats()

    if stats['total_items'] >= agent.max_items:
        # Export and filter old items
        exported = agent.export_memory()

        # Keep only recent items
        recent = sorted(
            exported,
            key=lambda x: x['last_access_time'],
            reverse=True
        )[:agent.max_items // 2]  # Keep 50%

        # Clear and reimport
        agent.clear_memory()
        agent.import_memory(recent)

        print(f"Evicted {len(exported) - len(recent)} old items")

    return agent.add(content, metadata)
```

### **Solution 4: Use Database Backend (Advanced)**

For >10K items, implement database-backed tiers:

```python
from cascading_agent.memory_tier import MemoryTier
import psycopg2
import numpy as np

class DatabaseTier(MemoryTier):
    """Tier backed by PostgreSQL with pgvector."""

    def __init__(self, config, connection_string):
        super().__init__(config)
        self.conn = psycopg2.connect(connection_string)
        # Implement search, add, etc. using database

    def search(self, query_embedding, top_k, threshold):
        # Use pgvector for similarity search
        # SELECT * FROM embeddings
        # ORDER BY embedding <-> %s
        # LIMIT %s
        pass
```

---

## Problem #3: Thread Safety

### **Issue**
No locking mechanisms, causing race conditions in concurrent applications.

**Severity:** 🟡 MEDIUM (50% probability if multi-threaded)

### **Symptoms**
- Occasional errors in multi-threaded apps
- Corrupted tier state
- Inconsistent statistics
- Data races

### **When It Matters**
- Web servers (Flask, FastAPI, Django)
- Multi-threaded applications
- Async/concurrent code
- Multiple agents in same process

### **Solution 1: Use ProductionAgent**

```python
from cascading_agent import ProductionAgent

# Thread-safe by default
agent = ProductionAgent(
    config=config,
    enable_thread_safety=True  # Default
)

# Safe to use from multiple threads
import threading

def worker():
    agent.add("Content from thread")
    results = agent.query("query")

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### **Solution 2: Manual Thread-Safe Wrapper**

```python
import threading
from cascading_agent import CascadingAgent

class ThreadSafeAgent(CascadingAgent):
    def __init__(self, config):
        super().__init__(config)
        self._lock = threading.RLock()  # Reentrant lock

    def add(self, *args, **kwargs):
        with self._lock:
            return super().add(*args, **kwargs)

    def query(self, *args, **kwargs):
        with self._lock:
            return super().query(*args, **kwargs)

    def clear_memory(self):
        with self._lock:
            return super().clear_memory()

# Use ThreadSafeAgent instead of CascadingAgent
agent = ThreadSafeAgent(config)
```

### **Solution 3: Process-Based Concurrency**

If thread locking isn't enough, use separate processes:

```python
from multiprocessing import Process, Queue
from cascading_agent import CascadingAgent

def agent_worker(query_queue, result_queue):
    """Run agent in separate process."""
    agent = CascadingAgent(config)

    while True:
        query = query_queue.get()
        if query is None:
            break

        results = agent.query(query)
        result_queue.put(results)

# Start worker process
query_q = Queue()
result_q = Queue()
p = Process(target=agent_worker, args=(query_q, result_q))
p.start()

# Use from main process
query_q.put("my query")
results = result_q.get()
```

### **Testing Thread Safety**

```python
import threading
import time

def stress_test_thread_safety(agent, num_threads=10, operations=100):
    """Test thread safety under load."""
    errors = []

    def worker(thread_id):
        try:
            for i in range(operations):
                agent.add(f"Content from thread {thread_id}, op {i}")
                agent.query(f"query {i}")
        except Exception as e:
            errors.append((thread_id, e))

    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(num_threads)
    ]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    print(f"Completed {num_threads * operations} operations in {elapsed:.2f}s")
    print(f"Errors: {len(errors)}")

    if errors:
        print("❌ Thread safety issues detected!")
        for tid, error in errors[:5]:
            print(f"  Thread {tid}: {error}")
    else:
        print("✅ Thread safety test passed")

# Run test
from cascading_agent import create_production_agent
agent = create_production_agent(enable_thread_safety=True)
stress_test_thread_safety(agent)
```

---

## Additional Hardening

### **Error Handling**

```python
from cascading_agent import ProductionAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='agent.log'
)

agent = ProductionAgent(
    config=config,
    log_level="INFO"  # DEBUG, INFO, WARNING, ERROR
)

# Errors are logged automatically
result = agent.add("")  # Empty content - returns None, logs error
results = agent.query("")  # Empty query - returns [], logs error
```

### **Input Validation**

```python
def safe_add(agent, content, metadata=None):
    """Add content with validation."""
    # Check content
    if not content or not isinstance(content, str):
        logging.error("Invalid content type")
        return None

    if len(content) > 10000:
        logging.warning(f"Content too long ({len(content)} chars), truncating")
        content = content[:10000]

    # Check metadata
    if metadata and not isinstance(metadata, dict):
        logging.error("Metadata must be dict")
        return None

    return agent.add(content, metadata)
```

### **Monitoring and Alerting**

```python
import time
from collections import deque

class MonitoredAgent(ProductionAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_times = deque(maxlen=1000)

    def query(self, *args, **kwargs):
        start = time.time()
        results = super().query(*args, **kwargs)
        elapsed = (time.time() - start) * 1000

        self.query_times.append(elapsed)

        # Alert on slow queries
        if elapsed > 1000:  # 1 second
            logging.warning(f"Slow query: {elapsed:.0f}ms")

        return results

    def get_performance_metrics(self):
        if not self.query_times:
            return {}

        times = list(self.query_times)
        return {
            "avg_ms": sum(times) / len(times),
            "p50_ms": sorted(times)[len(times) // 2],
            "p95_ms": sorted(times)[int(len(times) * 0.95)],
            "p99_ms": sorted(times)[int(len(times) * 0.99)],
            "max_ms": max(times)
        }
```

---

## Production Checklist

### **Before Deployment**

- [ ] **Embeddings**
  - [ ] Using real embeddings (not hash-based)
  - [ ] Embedding model tested and validated
  - [ ] Embedding dimensions match across all content

- [ ] **Memory**
  - [ ] Total capacity under 10,000 items
  - [ ] Monitoring enabled
  - [ ] Health checks implemented
  - [ ] Eviction strategy defined

- [ ] **Thread Safety**
  - [ ] Using ProductionAgent or manual locks
  - [ ] Thread safety tested under load
  - [ ] No race conditions observed

- [ ] **Error Handling**
  - [ ] Logging configured
  - [ ] Input validation added
  - [ ] Error recovery tested

- [ ] **Performance**
  - [ ] Query latency measured
  - [ ] Throughput tested
  - [ ] Bottlenecks identified

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] Load tests run
  - [ ] Edge cases covered

### **After Deployment**

- [ ] **Monitoring**
  - [ ] Health status checked regularly
  - [ ] Performance metrics tracked
  - [ ] Alerts configured
  - [ ] Logs reviewed

- [ ] **Maintenance**
  - [ ] Capacity monitored
  - [ ] Old data evicted periodically
  - [ ] Embeddings updated as needed
  - [ ] Performance tuned based on usage

---

## Example: Complete Production Setup

```python
from cascading_agent import create_production_agent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

# Create production agent
agent = create_production_agent(
    tier_capacities=[50, 500, 5000],
    max_items=10000,
    enable_thread_safety=True,
    log_level="INFO"
)

# Add health check endpoint (for monitoring)
def health_check():
    health = agent.get_health_status()
    return {
        "healthy": health['status'] not in ['CRITICAL'],
        "status": health['status'],
        "capacity": health['capacity_used'],
        "items": health['total_items']
    }

# Add safe wrapper functions
def safe_add(content, metadata=None):
    if not content:
        return None
    return agent.add(content, metadata)

def safe_query(query, **kwargs):
    if not query:
        return []
    return agent.query(query, **kwargs)

# Use in your application
if __name__ == "__main__":
    # Add content
    safe_add("Production-ready content")

    # Query
    results = safe_query("production ready")

    # Check health
    health = health_check()
    print(f"Health: {health}")
```

---

## Next Steps

1. **Start with ProductionAgent:** Use `create_production_agent()` for immediate fixes
2. **Test thoroughly:** Run stress tests and validate behavior
3. **Monitor in production:** Track health, performance, and capacity
4. **Scale appropriately:** Use database backend if >10K items needed
5. **Iterate:** Tune based on real usage patterns

For questions or issues, see [SUPPORT.md](../.github/SUPPORT.md).
