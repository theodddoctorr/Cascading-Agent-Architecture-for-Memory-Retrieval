"""
Main agent implementation for the cascading architecture.

Provides a high-level interface for interacting with the cascading
memory retrieval system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable
import numpy as np
from datetime import datetime

from .memory_tier import MemoryTier, TierConfig
from .retrieval import CascadingRetrieval, RetrievalStrategy


@dataclass
class AgentConfig:
    """Configuration for the cascading agent."""

    tier_configs: List[TierConfig]
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.SEQUENTIAL
    auto_promote: bool = True
    embedding_function: Optional[Callable[[str], np.ndarray]] = None
    default_top_k: int = 5
    default_threshold: float = 0.7


class CascadingAgent:
    """
    Main agent for cascading memory retrieval.

    Provides a high-level API for adding content, querying,
    and managing the multi-tier memory system.
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the cascading agent.

        Args:
            config: Agent configuration
        """
        self.config = config

        # Create memory tiers
        self.tiers = [
            MemoryTier(tier_config)
            for tier_config in config.tier_configs
        ]

        # Create retrieval system
        self.retrieval = CascadingRetrieval(
            tiers=self.tiers,
            strategy=config.retrieval_strategy,
            auto_promote=config.auto_promote
        )

        # Embedding function
        self.embedding_function = config.embedding_function or self._default_embedding

        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []

    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[np.ndarray] = None,
        item_id: Optional[str] = None
    ) -> str:
        """
        Add content to the memory system.

        Args:
            content: Text content to add
            metadata: Optional metadata dictionary
            embedding: Pre-computed embedding (computed if None)
            item_id: Unique ID (auto-generated if None)

        Returns:
            Item ID
        """
        # Generate ID if not provided
        if item_id is None:
            item_id = self._generate_id(content)

        # Compute embedding if not provided
        if embedding is None:
            embedding = self.embedding_function(content)

        # Add to slowest tier by default (will be promoted if accessed frequently)
        self.retrieval.add_item(
            item_id=item_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            target_tier=-1  # Slowest tier
        )

        return item_id

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        max_tiers: Optional[int] = None,
        return_embeddings: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Query the memory system.

        Args:
            query: Query text
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            max_tiers: Maximum number of tiers to search
            return_embeddings: Include embeddings in results

        Returns:
            List of result dictionaries
        """
        # Use defaults if not specified
        if top_k is None:
            top_k = self.config.default_top_k
        if threshold is None:
            threshold = self.config.default_threshold

        # Compute query embedding
        query_embedding = self.embedding_function(query)

        # Perform retrieval
        results = self.retrieval.retrieve(
            query_embedding=query_embedding,
            top_k=top_k,
            threshold=threshold,
            max_tiers=max_tiers
        )

        # Format results
        formatted_results = []
        for item_id, item, similarity, tier_name in results:
            result = {
                "item_id": item_id,
                "content": item.content,
                "similarity": float(similarity),
                "tier": tier_name,
                "metadata": item.metadata,
                "access_count": item.access_count,
                "last_accessed": datetime.fromtimestamp(item.last_access_time).isoformat()
            }

            if return_embeddings:
                result["embedding"] = item.embedding.tolist()

            formatted_results.append(result)

        # Record in conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": len(formatted_results),
            "top_similarity": formatted_results[0]["similarity"] if formatted_results else 0.0
        })

        return formatted_results

    def chat(
        self,
        message: str,
        context_k: int = 3,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Chat interface with memory-augmented responses.

        Args:
            message: User message
            context_k: Number of context items to retrieve
            threshold: Similarity threshold for context

        Returns:
            Response dictionary with context and answer
        """
        # Retrieve relevant context
        context = self.query(
            query=message,
            top_k=context_k,
            threshold=threshold
        )

        # In a real implementation, this would call an LLM
        # For now, return the retrieved context
        response = {
            "message": message,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }

        return response

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the agent.

        Returns:
            Statistics dictionary
        """
        stats = self.retrieval.get_stats()
        stats["conversation_history_length"] = len(self.conversation_history)

        return stats

    def get_tier_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all memory tiers.

        Returns:
            List of tier information dictionaries
        """
        return [tier.get_stats() for tier in self.tiers]

    def clear_memory(self):
        """Clear all memory tiers."""
        self.retrieval.clear_all_tiers()
        self.conversation_history.clear()

    def export_memory(self) -> List[Dict[str, Any]]:
        """
        Export all memory items.

        Returns:
            List of memory items with metadata
        """
        items = []
        for tier_idx, tier in enumerate(self.tiers):
            for item_id, item in tier.items.items():
                items.append({
                    "item_id": item_id,
                    "content": item.content,
                    "embedding": item.embedding.tolist(),
                    "metadata": item.metadata,
                    "tier": tier.config.name,
                    "tier_index": tier_idx,
                    "access_count": item.access_count,
                    "last_access_time": item.last_access_time,
                    "creation_time": item.creation_time
                })

        return items

    def import_memory(self, items: List[Dict[str, Any]]):
        """
        Import memory items.

        Args:
            items: List of item dictionaries (from export_memory)
        """
        for item_data in items:
            self.add(
                content=item_data["content"],
                metadata=item_data.get("metadata"),
                embedding=np.array(item_data["embedding"]),
                item_id=item_data["item_id"]
            )

    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for content."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _default_embedding(self, text: str) -> np.ndarray:
        """
        Default embedding function (simple hash-based).

        In production, replace with proper embedding model (e.g., OpenAI, HuggingFace).

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Simple hash-based embedding for demonstration
        # NOT suitable for production - use proper embedding models
        import hashlib

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 384-dimensional vector (similar to sentence transformers)
        embedding = np.array([
            float(b) / 255.0 - 0.5
            for b in hash_bytes
        ])

        # Pad/tile to desired dimension
        target_dim = 384
        while len(embedding) < target_dim:
            embedding = np.concatenate([embedding, embedding])

        embedding = embedding[:target_dim]

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def __repr__(self) -> str:
        """String representation of the agent."""
        total_items = sum(tier.size() for tier in self.tiers)
        return (
            f"CascadingAgent("
            f"tiers={len(self.tiers)}, "
            f"total_items={total_items}, "
            f"strategy={self.config.retrieval_strategy.value})"
        )
