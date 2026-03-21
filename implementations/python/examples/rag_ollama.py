#!/usr/bin/env python3
"""
RAG with Ollama + Cascading Agent

Combines cascading memory retrieval with Ollama local LLM to answer questions
using your own documents/chat logs as context.

Requirements:
    pip install sentence-transformers requests

    Ollama installed and running:
    https://ollama.ai

Usage:
    # Load documents and query with AI
    python rag_ollama.py path/to/documents --interactive

    # Use specific model
    python rag_ollama.py path/to/documents --model llama3 --interactive

    # Load chat logs
    python rag_ollama.py chatgpt.jsonl claude.jsonl --chat-logs --interactive
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cascading_agent import create_production_agent


class OllamaRAG:
    """RAG system using Ollama + Cascading Agent"""

    def __init__(self, model: str = "llama3", ollama_url: str = "http://localhost:11434"):
        """
        Initialize RAG system.

        Args:
            model: Ollama model name (llama3, mistral, etc.)
            ollama_url: Ollama API endpoint
        """
        self.model = model
        self.ollama_url = ollama_url
        self.agent = None

        # Check if Ollama is running
        if not self._check_ollama():
            print(f"⚠️  Warning: Cannot connect to Ollama at {ollama_url}")
            print(f"   Make sure Ollama is running: ollama serve")
            print(f"   And the model is available: ollama pull {model}")

    def _check_ollama(self) -> bool:
        """Check if Ollama is accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def initialize_agent(self, tier_capacities: List[int] = None, max_items: int = 100000):
        """Initialize the cascading agent with sentence-transformers."""
        print("🚀 Initializing cascading agent with sentence-transformers...")

        self.agent = create_production_agent(
            tier_capacities=tier_capacities or [100, 1000, 10000],
            max_items=max_items,
            enable_thread_safety=True,
            log_level="WARNING"
        )
        print("✅ Agent initialized with semantic search enabled")

    def load_files(self, file_paths: List[str], chunk_size: int = 500):
        """Load text files into memory."""
        if not self.agent:
            self.initialize_agent()

        total_chunks = 0

        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue

            print(f"   Loading: {file_path}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple chunking
                words = content.split()
                for i in range(0, len(words), chunk_size - 50):
                    chunk = ' '.join(words[i:i + chunk_size])
                    if chunk.strip():
                        self.agent.add(
                            content=chunk,
                            metadata={'file': os.path.basename(file_path)}
                        )
                        total_chunks += 1
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")

        print(f"✅ Loaded {total_chunks} chunks")

    def query_llm(self, prompt: str, context: str = "", stream: bool = False) -> str:
        """
        Query Ollama LLM with optional context.

        Args:
            prompt: User question
            context: Retrieved context from documents
            stream: Whether to stream the response

        Returns:
            LLM response
        """
        # Build full prompt with context
        if context:
            full_prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {prompt}

Answer:"""
        else:
            full_prompt = prompt

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": stream
                },
                timeout=120
            )

            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'response' in data:
                                chunk = data['response']
                                print(chunk, end='', flush=True)
                                full_response += chunk
                    print()  # Newline after streaming
                    return full_response
                else:
                    result = response.json()
                    return result.get('response', '')
            else:
                return f"Error: Ollama returned status {response.status_code}"

        except Exception as e:
            return f"Error querying Ollama: {e}"

    def ask(self, question: str, top_k: int = 5, use_context: bool = True, stream: bool = True) -> str:
        """
        Ask a question using RAG.

        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            use_context: Whether to use retrieved context
            stream: Whether to stream the response

        Returns:
            AI answer
        """
        if not self.agent:
            return "Error: Agent not initialized. Load documents first."

        # Retrieve relevant context
        context = ""
        if use_context:
            results = self.agent.query(question, top_k=top_k)

            if results:
                print(f"\n📚 Retrieved {len(results)} relevant chunks")
                context = "\n\n".join([
                    f"[Source: {r.get('metadata', {}).get('file', 'unknown')}]\n{r['content']}"
                    for r in results
                ])

        # Query LLM
        print(f"\n🤖 {self.model} is thinking...\n")
        return self.query_llm(question, context, stream=stream)


def main():
    parser = argparse.ArgumentParser(
        description='RAG with Ollama + Cascading Agent'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Files or directories to load'
    )
    parser.add_argument(
        '--model',
        default='llama3',
        help='Ollama model to use (default: llama3)'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama API URL'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of context chunks to retrieve'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive Q&A mode'
    )
    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='Disable streaming responses'
    )

    args = parser.parse_args()

    # Initialize RAG system
    rag = OllamaRAG(model=args.model, ollama_url=args.ollama_url)

    # Load files
    print(f"\n📚 Loading files...")
    rag.load_files(args.files)

    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("🔍 RAG Interactive Mode")
        print("="*60)
        print(f"Model: {args.model}")
        print("Ask questions about your documents!")
        print("Commands: 'quit', 'stats', 'no-context', 'with-context'\n")

        use_context = True

        while True:
            try:
                question = input("\n❓ Question: ").strip()

                if question.lower() in ('quit', 'exit', 'q'):
                    break

                if question.lower() == 'stats':
                    health = rag.agent.get_health_status()
                    print(f"\n📊 Agent Status:")
                    print(f"   Items: {health['total_items']}/{health['max_items']}")
                    print(f"   Capacity: {health['capacity_used']:.1%}")
                    print(f"   Queries: {health['total_queries']}")
                    continue

                if question.lower() == 'no-context':
                    use_context = False
                    print("🔴 Context retrieval disabled")
                    continue

                if question.lower() == 'with-context':
                    use_context = True
                    print("🟢 Context retrieval enabled")
                    continue

                if not question:
                    continue

                # Ask question
                answer = rag.ask(
                    question,
                    top_k=args.top_k,
                    use_context=use_context,
                    stream=not args.no_stream
                )

                if args.no_stream:
                    print(f"\n💡 Answer:\n{answer}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    else:
        # Demo questions
        demo_questions = [
            "What is this document about?",
            "Summarize the main points",
        ]

        print("\n" + "="*60)
        print("🔍 Demo Questions")
        print("="*60)

        for question in demo_questions:
            print(f"\n❓ {question}")
            answer = rag.ask(question, top_k=args.top_k, stream=False)
            print(f"💡 {answer}\n")

        print("\n💡 Tip: Use --interactive for Q&A mode")


if __name__ == '__main__':
    main()
