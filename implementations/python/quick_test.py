#!/usr/bin/env python3
"""
Quick Test - Verify the implementation works

This script performs basic sanity checks on the implementation.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("🧪 Cascading Agent Quick Test")
print("="*60)

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from cascading_agent import (
        CascadingAgent,
        ProductionAgent,
        create_production_agent,
        MemoryTier,
        TierConfig
    )
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create basic agent
print("\n2. Creating basic agent...")
try:
    from cascading_agent import AgentConfig
    config = AgentConfig(
        tier_configs=[
            TierConfig(name="fast", capacity=10),
            TierConfig(name="medium", capacity=50),
        ]
    )
    agent = CascadingAgent(config)
    print("   ✓ Basic agent created")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 3: Add content
print("\n3. Adding content...")
try:
    agent.add("The quick brown fox jumps over the lazy dog", item_id="doc1")
    agent.add("Python is a high-level programming language", item_id="doc2")
    agent.add("Machine learning involves training models on data", item_id="doc3")
    print("   ✓ Added 3 documents")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 4: Query content
print("\n4. Testing query...")
try:
    results = agent.query("programming", top_k=2)
    if results:
        print(f"   ✓ Query returned {len(results)} results")
        print(f"   Top result: {results[0]['content'][:50]}...")
    else:
        print("   ⚠ Query returned no results (expected with hash embeddings)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 5: Production agent
print("\n5. Testing ProductionAgent...")
try:
    prod_agent = create_production_agent(
        tier_capacities=[10, 50, 100],
        max_items=200,
        enable_thread_safety=True
    )
    print("   ✓ ProductionAgent created")

    # Add some content
    prod_agent.add("Test content for production agent")

    # Check health
    health = prod_agent.get_health_status()
    print(f"   ✓ Health status: {health['status']}")
    print(f"   ✓ Capacity used: {health['capacity_used']:.1%}")

except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 6: Memory export/import
print("\n6. Testing export/import...")
try:
    exported = agent.export_memory()
    print(f"   ✓ Exported memory: {len(exported)} bytes")

    # Create new agent and import
    new_agent = CascadingAgent(config)
    new_agent.import_memory(exported)
    print("   ✓ Memory imported successfully")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 7: Chat interface
print("\n7. Testing chat interface...")
try:
    response = agent.chat("What do you know about programming?")
    print(f"   ✓ Chat response generated ({len(response)} chars)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("✅ All tests passed!")
print("="*60)
print("\n💡 Next steps:")
print("   - Try examples/production_ready.py for full features")
print("   - Use examples/file_loader.py to test with your own files")
print("   - Install sentence-transformers for better embeddings:")
print("     pip install sentence-transformers")
print("\n📚 Documentation:")
print("   - README.md - Quick start and API reference")
print("   - docs/IMPLEMENTATION_GUIDE.md - Comprehensive guide")
print("   - docs/PRODUCTION_HARDENING.md - Production deployment")
