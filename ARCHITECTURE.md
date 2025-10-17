# 🏗️ Enhanced Emotional RAG - System Architecture

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER MESSAGE                                │
│                    "I feel lonely today"                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: EMOTION DETECTION                                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ RoBERTa Model (cardiffnlp/twitter-roberta-base-emotion)        │ │
│  │ Output: "sadness" (confidence: 0.87)                           │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: EMOTION-AWARE RETRIEVAL                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ A. Semantic Embedding (Sentence Transformers)                  │ │
│  │    "lonely" → [0.23, -0.45, 0.67, ...]                         │ │
│  │                                                                 │ │
│  │ B. Query ChromaDB (n=10 candidates)                            │ │
│  │    ┌─────────────────────────────────────────────────────────┐│ │
│  │    │ Doc 1: "I miss my friends" (emotion: sadness)           ││ │
│  │    │ Doc 2: "Feeling isolated" (emotion: sadness)            ││ │
│  │    │ Doc 3: "Great day today!" (emotion: joy)                ││ │
│  │    │ Doc 4: "I'm anxious about work" (emotion: fear)         ││ │
│  │    │ ...                                                      ││ │
│  │    └─────────────────────────────────────────────────────────┘│ │
│  │                                                                 │ │
│  │ C. Re-rank with Hybrid Scoring                                 │ │
│  │    ┌─────────────────────────────────────────────────────────┐│ │
│  │    │ For each document:                                      ││ │
│  │    │                                                          ││ │
│  │    │ score = 0.6 × semantic_similarity                       ││ │
│  │    │       + 0.4 × emotion_similarity                        ││ │
│  │    │       + 0.1 × recency_boost                             ││ │
│  │    │                                                          ││ │
│  │    │ Doc 1: 0.6×0.85 + 0.4×1.0 + 0.1×0.9 = 1.00 ✅          ││ │
│  │    │ Doc 2: 0.6×0.78 + 0.4×1.0 + 0.1×0.7 = 0.94 ✅          ││ │
│  │    │ Doc 4: 0.6×0.72 + 0.4×0.7 + 0.1×0.8 = 0.79 ✅          ││ │
│  │    │ Doc 3: 0.6×0.81 + 0.4×0.3 + 0.1×0.6 = 0.61 ❌          ││ │
│  │    └─────────────────────────────────────────────────────────┘│ │
│  │                                                                 │ │
│  │ D. Return Top 5                                                 │ │
│  │    ["I miss my friends", "Feeling isolated", ...]              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: CONVERSATION STATE RETRIEVAL                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Recent Turns (Last 3):                                         │ │
│  │ ┌────────────────────────────────────────────────────────────┐│ │
│  │ │ Turn 1: User (joy): "Got a promotion!"                     ││ │
│  │ │         Bot: "That's wonderful! Tell me more..."           ││ │
│  │ │                                                             ││ │
│  │ │ Turn 2: User (surprise): "It's a big responsibility"      ││ │
│  │ │         Bot: "Change brings new challenges..."            ││ │
│  │ │                                                             ││ │
│  │ │ Turn 3: User (sadness): "I feel lonely today"             ││ │
│  │ └────────────────────────────────────────────────────────────┘│ │
│  │                                                                 │ │
│  │ Emotional Journey: joy → surprise → sadness                    │ │
│  │ Dominant Emotion: sadness                                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: CHARACTER-AWARE PROMPT BUILDING                            │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ # YOUR ROLE                                                    │ │
│  │ Name: Aria                                                     │ │
│  │ Personality: empathetic, supportive, non-judgmental           │ │
│  │ Emotional Intelligence: 90%                                    │ │
│  │                                                                 │ │
│  │ # EMOTIONAL CONTEXT                                            │ │
│  │ User emotion: sadness                                          │ │
│  │ Empathy Level: 95%                                             │ │
│  │ Response Style: deeply empathetic, validating, gentle         │ │
│  │                                                                 │ │
│  │ # RELEVANT MEMORIES                                            │ │
│  │ [Retrieved context from RAG]                                   │ │
│  │                                                                 │ │
│  │ # RECENT CONVERSATION                                          │ │
│  │ [Last 3 turns from conversation state]                         │ │
│  │                                                                 │ │
│  │ # CURRENT INTERACTION                                          │ │
│  │ User: I feel lonely today                                      │ │
│  │                                                                 │ │
│  │ # YOUR RESPONSE                                                │ │
│  │ Respond as Aria, maintaining character traits...              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: LLM GENERATION (Gemini)                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Model: gemini-1.5-flash                                        │ │
│  │ Temperature: 0.8 (creative but consistent)                     │ │
│  │ Max Tokens: 500                                                 │ │
│  │                                                                 │ │
│  │ → "I hear the sadness in your words, and I want you to know   │ │
│  │    that's completely valid. Earlier, you shared the joy of    │ │
│  │    your promotion, and now you're experiencing this loneliness│ │
│  │    - that's a real emotional shift. What do you think is      │ │
│  │    contributing to these feelings of isolation?"               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: MULTI-LAYER MEMORY STORAGE                                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ A. ChromaDB (Vector Store)                                     │ │
│  │    ├─ Document: "I feel lonely today"                          │ │
│  │    ├─ Embedding: [0.23, -0.45, 0.67, ...]                      │ │
│  │    ├─ Metadata: {emotion: "sadness", speaker: "user",          │ │
│  │    │             timestamp: 1729180234, bot_reply: "..."}      │ │
│  │    └─ ID: "1729180234_a3f7b2c9"                                │ │
│  │                                                                 │ │
│  │ B. JSON Memory (data/memory.json)                              │ │
│  │    ├─ Full conversation history                                │ │
│  │    └─ {user_text, user_emotion, bot_reply}                     │ │
│  │                                                                 │ │
│  │ C. Conversation State (data/conversation_state.json)           │ │
│  │    ├─ Last 10 turns                                            │ │
│  │    ├─ Emotion history: [joy, surprise, sadness, ...]           │ │
│  │    └─ Dominant emotion: sadness                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  RESPONSE TO USER                                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ {                                                              │ │
│  │   "reply": "I hear the sadness in your words...",             │ │
│  │   "user_emotion": "sadness",                                  │ │
│  │   "retrieved_context": ["I miss my friends", ...],            │ │
│  │   "emotional_summary": "We've discussed sadness 3 times...",  │ │
│  │   "conversation_stats": {                                     │ │
│  │     "turn_count": 3,                                          │ │
│  │     "dominant_emotion": "sadness",                            │ │
│  │     "emotional_journey": "joy → surprise → sadness"           │ │
│  │   },                                                          │ │
│  │   "character": "Aria"                                         │ │
│  │ }                                                              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Innovations

### 1. **Emotion Similarity Scoring**
```
Same Emotion:        1.0  (perfect match)
Same Group:          0.7  (high similarity)
Different Groups:    0.3  (baseline similarity)

Groups:
- Negative: [sadness, anger, fear, disgust]
- Positive: [joy, happiness, excitement, love]
- Neutral:  [surprise, neutral, curiosity]
```

### 2. **Hybrid Retrieval Score**
```python
score = (1 - emotion_weight) × semantic_score 
        + emotion_weight × emotion_score 
        + 0.1 × recency_score

# Default: emotion_weight = 0.4
# Adjustable per request
```

### 3. **Character Consistency**
```
Persona → Response Patterns → Empathy Levels → Speaking Style
    ↓           ↓                    ↓                ↓
  Traits    Guidance per         Adjustable      Natural
            emotion type         per emotion     language
```

### 4. **Three-Layer Memory**
```
Vector DB          JSON Log           State Tracker
    ↓                  ↓                    ↓
Semantic +         Full history      Emotional arc +
Emotional search                     Recent context
```

## Data Flow Example

### Input
```json
{
  "message": "I feel lonely today",
  "emotion_weight": 0.4,
  "use_recent_context": true
}
```

### Processing
1. **Emotion Detection**: `"sadness"` (0.87 confidence)
2. **Retrieval**: 5 docs (4 with sadness/fear, 1 neutral)
3. **State**: Recent history shows joy → surprise → sadness
4. **Character**: Aria (empathy 95% for sadness)
5. **Prompt**: 1450 chars with all context
6. **Generation**: ~200 tokens, temp 0.8
7. **Storage**: 3 locations (vector, JSON, state)

### Output
```json
{
  "reply": "Emotionally aware, character-consistent response",
  "user_emotion": "sadness",
  "retrieved_context": [...],
  "emotional_summary": "...",
  "conversation_stats": {...}
}
```

## Performance Characteristics

- **Retrieval Time**: ~50-100ms (embedding + DB query + re-ranking)
- **LLM Generation**: ~1-2s (depends on Gemini API)
- **Total Response**: ~1.5-2.5s
- **Memory Growth**: Linear with conversation turns
- **Storage**: ~1KB per turn

## Scalability Considerations

### Current Design (Single User)
- In-memory conversation state
- Single ChromaDB collection
- File-based state persistence

### Multi-User Scaling (Future)
- Session-based state management
- Per-user ChromaDB collections
- Redis/Database for state
- Load balancing for LLM calls

---

This architecture creates a truly **emotionally intelligent AI** that:
✅ Remembers emotions, not just words
✅ Maintains consistent personality
✅ Tracks conversation context
✅ Adapts to emotional moments
✅ Builds long-term relationships
