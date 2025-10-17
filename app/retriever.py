"""Enhanced emotional RAG retrieval with multi-strategy memory access.

This module implements emotion-aware retrieval that combines:
1. Semantic similarity (embedding-based)
2. Emotional resonance (same/related emotions)
3. Temporal relevance (recent context)
"""

from sentence_transformers import SentenceTransformer
import chromadb
import uuid
import time
from typing import List, Dict, Tuple, Optional

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="data/embeddings")
collection = chroma_client.get_or_create_collection(name="emotional_memory")

# Emotion similarity groups - emotions in same group are considered related
EMOTION_GROUPS = {
    "negative": ["sadness", "anger", "fear", "disgust"],
    "positive": ["joy", "happiness", "excitement", "love"],
    "neutral": ["surprise", "neutral", "curiosity"],
}

def get_emotion_similarity(emotion1: str, emotion2: str) -> float:
    """Calculate similarity score between two emotions (0.0 to 1.0)."""
    emotion1 = emotion1.lower()
    emotion2 = emotion2.lower()
    
    # Same emotion = perfect match
    if emotion1 == emotion2:
        return 1.0
    
    # Check if emotions are in same group
    for group in EMOTION_GROUPS.values():
        if emotion1 in group and emotion2 in group:
            return 0.7  # High similarity within group
    
    # Different groups
    return 0.3  # Low but non-zero base similarity


def add_to_memory(text: str, emotion: str, speaker: str = "user", bot_reply: Optional[str] = None):
    """
    Stores text + emotion embedding for future retrieval with enhanced metadata.
    
    Args:
        text: The text to store
        emotion: Detected emotion label
        speaker: Who said it ("user" or "bot")
        bot_reply: If storing user message, optionally include the bot's response
    """
    embedding = model.encode(text).tolist()
    timestamp = int(time.time() * 1000)
    doc_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"
    
    metadata = {
        "emotion": emotion.lower(),
        "speaker": speaker,
        "timestamp": timestamp,
    }
    if bot_reply:
        metadata["bot_reply"] = bot_reply
    
    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


def retrieve_context(
    query: str, 
    emotion: str, 
    top_k: int = 5,
    emotion_weight: float = 0.4,
    include_recent: bool = True
) -> List[str]:
    """
    Enhanced retrieval with emotion-awareness and hybrid ranking.
    
    Strategy:
    1. Retrieve more candidates than needed (top_k * 2)
    2. Re-rank based on:
       - Semantic similarity (from ChromaDB)
       - Emotional similarity
       - Recency (optional)
    3. Return top_k results
    
    Args:
        query: User's query text
        emotion: Detected emotion of current query
        top_k: Number of results to return
        emotion_weight: Weight for emotional similarity (0.0-1.0)
        include_recent: Whether to boost recent memories
    
    Returns:
        List of relevant context strings
    """
    query_embedding = model.encode(query).tolist()
    
    # Retrieve more candidates for re-ranking
    n_candidates = max(top_k * 2, 10)
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"]
    )
    
    if not results["documents"][0]:
        return []
    
    # Re-rank based on emotional similarity
    scored_results = []
    current_time = int(time.time() * 1000)
    
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i] if "distances" in results else 0
        
        # Semantic score (lower distance = higher similarity)
        semantic_score = 1.0 / (1.0 + distance)
        
        # Emotional similarity score
        doc_emotion = metadata.get("emotion", "neutral")
        emotion_score = get_emotion_similarity(emotion, doc_emotion)
        
        # Recency score (exponential decay, half-life of ~1 hour)
        recency_score = 1.0
        if include_recent and "timestamp" in metadata:
            age_ms = current_time - metadata["timestamp"]
            age_hours = age_ms / (1000 * 60 * 60)
            recency_score = 0.5 ** (age_hours / 1.0)  # Decay with 1 hour half-life
        
        # Combined score with weights
        combined_score = (
            (1.0 - emotion_weight) * semantic_score +
            emotion_weight * emotion_score +
            0.1 * recency_score  # Small recency boost
        )
        
        scored_results.append((doc, combined_score, metadata))
    
    # Sort by combined score (descending)
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top_k documents
    return [doc for doc, score, metadata in scored_results[:top_k]]


def get_emotional_context_summary(emotion: str, top_k: int = 3) -> str:
    """
    Get a summary of how the conversation has dealt with this emotion before.
    
    Useful for understanding emotional patterns in the conversation history.
    """
    # Query for similar emotional moments without semantic filtering
    results = collection.query(
        query_embeddings=[model.encode(emotion).tolist()],
        n_results=top_k,
        where={"emotion": emotion.lower()}
    )
    
    if not results["documents"][0]:
        return f"This is the first time we're exploring {emotion} together."
    
    count = len(results["documents"][0])
    return f"We've discussed {emotion} {count} time(s) before in our conversation."
