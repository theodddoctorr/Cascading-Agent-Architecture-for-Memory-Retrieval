#!/usr/bin/env python3
"""
RAG with LM Studio + Cascading Agent

Combines cascading memory retrieval with LM Studio local LLM to answer questions
using your own documents/chat logs as context.

Requirements:
    pip install sentence-transformers requests

    LM Studio running with local server enabled

Usage:
    # Load documents and query with AI
    python rag_lmstudio.py path/to/documents --interactive

    # Custom LM Studio port
    python rag_lmstudio.py path/to/documents --port 1234 --interactive
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


class LMStudioRAG:
    """RAG system using LM Studio + Cascading Agent"""

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """
        Initialize RAG system.

        Args:
            base_url: LM Studio API endpoint (OpenAI-compatible)
        """
        self.base_url = base_url
        self.agent = None

        # Check if LM Studio is running
        if not self._check_lmstudio():
            print(f"⚠️  Warning: Cannot connect to LM Studio at {base_url}")
            print(f"   Make sure LM Studio is running with local server enabled")
            print(f"   (In LM Studio: Go to Local Server tab and click Start)")

    def _check_lmstudio(self) -> bool:
        """Check if LM Studio is accessible."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_model_name(self) -> str:
        """Get the currently loaded model name from LM Studio."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0]['id']
        except:
            pass
        return "unknown-model"

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

    def query_llm(
        self,
        prompt: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False
    ) -> str:
        """
        Query LM Studio using OpenAI-compatible API.

        Args:
            prompt: User question
            context: Retrieved context from documents
            temperature: Sampling temperature
            max_tokens: Maximum response length
            stream: Whether to stream the response

        Returns:
            LLM response
        """
        # Build messages with context
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful assistant. Use the following context to answer questions:\n\n{context}"
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                },
                timeout=120,
                stream=stream
            )

            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            chunk = delta['content']
                                            print(chunk, end='', flush=True)
                                            full_response += chunk
                                except json.JSONDecodeError:
                                    pass
                    print()  # Newline after streaming
                    return full_response
                else:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    return "No response from model"
            else:
                return f"Error: LM Studio returned status {response.status_code}"

        except Exception as e:
            return f"Error querying LM Studio: {e}"

    def ask(
        self,
        question: str,
        top_k: int = 5,
        use_context: bool = True,
        stream: bool = True,
        temperature: float = 0.7
    ) -> str:
        """
        Ask a question using RAG.

        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            use_context: Whether to use retrieved context
            stream: Whether to stream the response
            temperature: LLM temperature

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
        model_name = self.get_model_name()
        print(f"\n🤖 {model_name} is thinking...\n")
        return self.query_llm(question, context, temperature=temperature, stream=stream)


def main():
    parser = argparse.ArgumentParser(
        description='RAG with LM Studio + Cascading Agent'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Files or directories to load'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=1234,
        help='LM Studio port (default: 1234)'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of context chunks to retrieve'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='LLM temperature (default: 0.7)'
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
    base_url = f"http://localhost:{args.port}/v1"
    rag = LMStudioRAG(base_url=base_url)

    # Load files
    print(f"\n📚 Loading files...")
    rag.load_files(args.files)

    # Interactive mode
    if args.interactive:
        print("\n" + "="*60)
        print("🔍 RAG Interactive Mode (LM Studio)")
        print("="*60)
        model_name = rag.get_model_name()
        print(f"Model: {model_name}")
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
                    stream=not args.no_stream,
                    temperature=args.temperature
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
