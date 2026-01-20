"""
File Loader Example - Load and query your own documents

This example shows how to:
1. Load files from disk (text, markdown, code, etc.)
2. Chunk them into manageable pieces
3. Add them to the agent
4. Query and retrieve relevant information

Usage:
    python file_loader.py /path/to/directory
    python file_loader.py file1.txt file2.md file3.py
"""

import sys
import os
from pathlib import Path
from typing import List, Dict
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cascading_agent import create_production_agent


def load_file(file_path: str) -> str:
    """Load a text file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return None
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for better retrieval."""
    if not text:
        return []

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks


def get_files_from_directory(directory: str, extensions: tuple = None) -> List[str]:
    """Recursively get all files from a directory."""
    if extensions is None:
        # Default text-based extensions
        extensions = ('.txt', '.md', '.py', '.js', '.java', '.c', '.cpp',
                     '.h', '.hpp', '.rs', '.go', '.rb', '.sh', '.yaml',
                     '.yml', '.json', '.xml', '.html', '.css', '.rst')

    files = []
    for root, dirs, filenames in os.walk(directory):
        # Skip hidden directories and common build/cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.')
                   and d not in ('node_modules', '__pycache__', 'venv', 'env',
                                'build', 'dist', '.git')]

        for filename in filenames:
            if filename.endswith(extensions):
                files.append(os.path.join(root, filename))

    return files


def main():
    parser = argparse.ArgumentParser(
        description='Load files into cascading agent memory and query them'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='Files or directories to load'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='Number of words per chunk (default: 500)'
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

    args = parser.parse_args()

    # Create production agent
    print("🚀 Creating production agent...")
    agent = create_production_agent(
        tier_capacities=[100, 1000, 10000],
        max_items=50000,
        enable_thread_safety=True,
        log_level="WARNING"  # Less verbose for file loading
    )

    # Collect all files to process
    all_files = []
    for path in args.paths:
        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            print(f"📁 Scanning directory: {path}")
            all_files.extend(get_files_from_directory(path))
        else:
            print(f"⚠️  Path not found: {path}")

    if not all_files:
        print("❌ No files found to load")
        return

    print(f"\n📚 Loading {len(all_files)} files...")

    # Load and chunk files
    total_chunks = 0
    file_metadata = {}

    for file_path in all_files:
        print(f"   Loading: {file_path}")
        content = load_file(file_path)

        if content:
            chunks = chunk_text(content, chunk_size=args.chunk_size)

            # Add each chunk with metadata
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path}:chunk_{i}"
                agent.add(
                    content=chunk,
                    item_id=chunk_id,
                    metadata={
                        'file_path': file_path,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'file_type': os.path.splitext(file_path)[1]
                    }
                )

            total_chunks += len(chunks)
            file_metadata[file_path] = len(chunks)

    print(f"\n✅ Loaded {total_chunks} chunks from {len(all_files)} files")

    # Show health status
    health = agent.get_health_status()
    print(f"📊 Memory status: {health['status']}")
    print(f"   Capacity used: {health['capacity_used']:.1%}")
    print(f"   Total items: {health['total_items']}/{health['max_items']}")

    # Interactive query mode
    if args.interactive:
        print("\n" + "="*60)
        print("🔍 Interactive Query Mode")
        print("="*60)
        print("Enter your queries (or 'quit' to exit):\n")

        while True:
            try:
                query = input("Query: ").strip()

                if query.lower() in ('quit', 'exit', 'q'):
                    break

                if not query:
                    continue

                # Query the agent
                results = agent.query(query, top_k=args.top_k)

                print(f"\n📋 Found {len(results)} results:\n")

                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    file_path = metadata.get('file_path', 'Unknown')
                    chunk_idx = metadata.get('chunk_index', '?')
                    score = result.get('score', 0)

                    print(f"{i}. {file_path} (chunk {chunk_idx}) - Score: {score:.4f}")
                    print(f"   {result['content'][:200]}...")
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
            "What is this project about?",
            "How does the implementation work?",
            "What are the main components?"
        ]

        for query in demo_queries:
            print(f"\nQuery: {query}")
            results = agent.query(query, top_k=3)

            if results:
                print(f"Top result from: {results[0].get('metadata', {}).get('file_path', 'Unknown')}")
                print(f"Score: {results[0].get('score', 0):.4f}")
                print(f"Content: {results[0]['content'][:150]}...")
            else:
                print("No results found")

        print("\n💡 Tip: Use --interactive flag for interactive queries")


if __name__ == '__main__':
    main()
