#!/usr/bin/env python3
"""
Chat Log Loader - Load JSONL chat logs into cascading agent memory

This script is specifically designed for ChatGPT and Claude chat logs in JSONL format.
It parses the conversation structure and makes them searchable.

Usage:
    python chat_log_loader.py chatgpt.jsonl claude.jsonl --interactive
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cascading_agent import create_production_agent


def parse_jsonl(file_path: str) -> List[Dict]:
    """Parse a JSONL file and return list of records."""
    records = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping line {line_num} in {file_path}: {e}")

    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

    return records


def parse_json(file_path: str) -> Optional[Dict]:
    """Parse a regular JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None


def extract_messages_from_record(record: Dict, source_file: str) -> List[Dict]:
    """
    Extract individual messages from a chat record.

    Handles different formats from ChatGPT and Claude.
    """
    messages = []

    # Try to detect format and extract messages
    # ChatGPT format typically has 'mapping' or 'messages'
    # Claude format may vary

    # Format 1: mapping with message objects
    if 'mapping' in record:
        for msg_id, msg_data in record['mapping'].items():
            if 'message' in msg_data and msg_data['message']:
                msg = msg_data['message']

                role = msg.get('author', {}).get('role', 'unknown')
                content_parts = msg.get('content', {}).get('parts', [])

                if content_parts:
                    content = '\n'.join(str(part) for part in content_parts if part)

                    if content.strip():
                        messages.append({
                            'role': role,
                            'content': content,
                            'timestamp': msg.get('create_time'),
                            'message_id': msg.get('id'),
                            'source': source_file
                        })

    # Format 2: direct messages array
    elif 'messages' in record:
        for msg in record['messages']:
            if isinstance(msg, dict):
                role = msg.get('role', msg.get('author', {}).get('role', 'unknown'))
                content = msg.get('content', '')

                if isinstance(content, dict):
                    content = content.get('text', str(content))

                if content and str(content).strip():
                    messages.append({
                        'role': role,
                        'content': str(content),
                        'timestamp': msg.get('created_at', msg.get('timestamp')),
                        'message_id': msg.get('id'),
                        'source': source_file
                    })

    # Format 3: conversation structure
    elif 'conversation' in record:
        conv = record['conversation']
        if isinstance(conv, list):
            for msg in conv:
                if 'text' in msg or 'content' in msg:
                    messages.append({
                        'role': msg.get('role', 'unknown'),
                        'content': msg.get('text', msg.get('content', '')),
                        'timestamp': msg.get('timestamp'),
                        'message_id': msg.get('id'),
                        'source': source_file
                    })

    return messages


def format_timestamp(ts) -> str:
    """Format timestamp to readable string."""
    if not ts:
        return "unknown time"

    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts)
            return dt.strftime("%Y-%m-%d %H:%M")
        return str(ts)
    except:
        return str(ts)


def main():
    parser = argparse.ArgumentParser(
        description='Load chat logs (JSONL/JSON) into cascading agent memory'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='JSONL or JSON chat log files to load'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of results to return (default: 5)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive query mode after loading'
    )
    parser.add_argument(
        '--show-sample',
        action='store_true',
        help='Show sample messages from loaded data'
    )

    args = parser.parse_args()

    # Create production agent
    print("🚀 Creating production agent for chat logs...")
    agent = create_production_agent(
        tier_capacities=[100, 1000, 10000],
        max_items=100000,  # Chat logs can be large
        enable_thread_safety=True,
        log_level="WARNING"
    )

    total_messages = 0
    total_records = 0
    file_stats = {}

    print(f"\n📚 Loading {len(args.files)} chat log file(s)...\n")

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"   Processing: {file_path}")

        # Determine file type
        if file_path.endswith('.jsonl'):
            records = parse_jsonl(file_path)
        elif file_path.endswith('.json'):
            data = parse_json(file_path)
            # If it's a single conversation, wrap in list
            records = [data] if data else []
        else:
            print(f"   ⚠️  Unknown file type (expected .jsonl or .json)")
            continue

        if not records:
            print(f"   ⚠️  No records found")
            continue

        total_records += len(records)
        file_messages = 0

        # Process each record
        for i, record in enumerate(records):
            messages = extract_messages_from_record(record, os.path.basename(file_path))

            # Add each message to agent
            for msg in messages:
                if msg['content'].strip():
                    item_id = f"{file_path}:record_{i}:msg_{msg.get('message_id', file_messages)}"

                    agent.add(
                        content=msg['content'],
                        item_id=item_id,
                        metadata={
                            'role': msg['role'],
                            'timestamp': format_timestamp(msg.get('timestamp')),
                            'source_file': msg['source'],
                            'message_id': msg.get('message_id'),
                            'record_index': i
                        }
                    )
                    file_messages += 1
                    total_messages += 1

        file_stats[file_path] = file_messages
        print(f"   ✓ Loaded {file_messages} messages from {len(records)} record(s)")

    print(f"\n✅ Total: {total_messages} messages from {total_records} records")

    # Show health status
    health = agent.get_health_status()
    print(f"📊 Memory status: {health['status']}")
    print(f"   Capacity used: {health['capacity_used']:.1%}")
    print(f"   Total items: {health['total_items']}/{health['max_items']}")

    # Show sample if requested
    if args.show_sample and total_messages > 0:
        print("\n" + "="*60)
        print("📝 Sample Messages")
        print("="*60)

        sample_query = agent.query("", top_k=3)  # Get any 3 items
        for i, result in enumerate(sample_query[:3], 1):
            meta = result.get('metadata', {})
            print(f"\n{i}. [{meta.get('role', 'unknown')}] at {meta.get('timestamp', '?')}")
            print(f"   {result['content'][:150]}...")

    # Interactive query mode
    if args.interactive:
        print("\n" + "="*60)
        print("🔍 Interactive Chat Log Search")
        print("="*60)
        print("Search your chat history!")
        print("Examples:")
        print("  - 'API implementation'")
        print("  - 'error handling'")
        print("  - 'how to use Python'")
        print("\nEnter your queries (or 'quit' to exit):\n")

        while True:
            try:
                query = input("Search: ").strip()

                if query.lower() in ('quit', 'exit', 'q'):
                    break

                if not query:
                    continue

                # Query the agent
                results = agent.query(query, top_k=args.top_k)

                if not results:
                    print("No results found. Try a different query.\n")
                    continue

                print(f"\n📋 Found {len(results)} result(s):\n")

                for i, result in enumerate(results, 1):
                    meta = result.get('metadata', {})
                    role = meta.get('role', 'unknown')
                    timestamp = meta.get('timestamp', '?')
                    source = meta.get('source_file', 'unknown')
                    score = result.get('score', 0)

                    print(f"{i}. [{role}] from {source} at {timestamp}")
                    print(f"   Score: {score:.4f}")

                    content = result['content']
                    # Show first 200 chars or full if shorter
                    if len(content) > 200:
                        print(f"   {content[:200]}...")
                        print(f"   ({len(content)} total characters)")
                    else:
                        print(f"   {content}")
                    print()

            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    else:
        # Demo queries if not interactive
        print("\n" + "="*60)
        print("🔍 Example Queries")
        print("="*60)

        demo_queries = [
            "Python code",
            "error handling",
            "implementation"
        ]

        for query in demo_queries:
            print(f"\nQuery: '{query}'")
            results = agent.query(query, top_k=2)

            if results:
                meta = results[0].get('metadata', {})
                print(f"  Top result: [{meta.get('role', '?')}] from {meta.get('source_file', '?')}")
                print(f"  Score: {results[0].get('score', 0):.4f}")
                print(f"  Preview: {results[0]['content'][:100]}...")
            else:
                print("  No results")

        print("\n💡 Tip: Use --interactive flag for interactive search")
        print("💡 Tip: Install sentence-transformers for better results:")
        print("        pip install sentence-transformers")


if __name__ == '__main__':
    main()
