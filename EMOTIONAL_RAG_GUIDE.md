# 🎭 Enhanced Emotional RAG System

An emotionally intelligent AI companion with RAG-powered memory, character consistency, and emotion-aware retrieval.

## 🌟 Key Features

### 1. **Multi-Dimensional Emotional RAG**
- **Hybrid Retrieval**: Combines semantic similarity + emotional resonance + temporal relevance
- **Emotion-Weighted Scoring**: Prioritizes memories with similar emotional context
- **Adaptive Context**: Retrieves relevant past conversations based on current emotional state

### 2. **Character Consistency**
- **Persistent Persona**: AI maintains consistent personality traits across conversations
- **Emotional Response Patterns**: Different response styles for different emotions
- **Configurable Empathy**: Adjustable empathy levels per emotion type

### 3. **Conversation State Tracking**
- **Emotional Arc**: Tracks emotional journey throughout conversation
- **Context Continuity**: Maintains recent conversation history for coherent responses
- **Dominant Emotion**: Identifies overall emotional theme of conversation

### 4. **Advanced Emotion Detection**
- Uses `cardiffnlp/twitter-roberta-base-emotion` for accurate emotion classification
- Supports: sadness, joy, anger, fear, surprise, and more
- Real-time emotion tracking and analysis

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
    ┌────▼─────────────────────────────┐
    │  1. Emotion Detection            │
    │  (RoBERTa-based classifier)      │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  2. Emotional RAG Retrieval      │
    │  • Semantic similarity           │
    │  • Emotional resonance           │
    │  • Temporal relevance            │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  3. Conversation State           │
    │  • Recent history                │
    │  • Emotional journey             │
    │  • Dominant emotion              │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  4. Character-Aware LLM          │
    │  • Persona consistency           │
    │  • Emotion-specific guidance     │
    │  • Enhanced prompt engineering   │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  5. Multi-System Memory Storage  │
    │  • Vector DB (ChromaDB)          │
    │  • JSON conversation log         │
    │  • Conversation state tracker    │
    └──────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Set up your API key
export GEMINI_API_KEY="your-api-key-here"
```

### Running the Server

```bash
uv run fastapi dev app/main.py
```

### API Endpoints

#### 1. **Chat** (Main Endpoint)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I feel lonely today.",
    "emotion_weight": 0.4,
    "use_recent_context": true
  }'
```

**Response:**
```json
{
  "reply": "I hear the sadness in your words...",
  "user_emotion": "sadness",
  "retrieved_context": ["previous similar moments..."],
  "emotional_summary": "We've discussed sadness 2 time(s) before...",
  "conversation_stats": {
    "turn_count": 5,
    "dominant_emotion": "sadness",
    "emotional_journey": "neutral → joy → sadness → sadness → sadness"
  },
  "character": "Aria"
}
```

#### 2. **Get Conversation State**
```bash
curl http://127.0.0.1:8000/conversation/state
```

#### 3. **Reset Conversation**
```bash
curl -X POST http://127.0.0.1:8000/conversation/reset
```

#### 4. **Get Character Info**
```bash
curl http://127.0.0.1:8000/character
```

## 🎨 Customizing the Character

Edit `app/character.py` to customize the AI persona:

```python
from app.character import CharacterPersona, EmotionalResponsePattern

my_character = CharacterPersona(
    name="Your Character Name",
    core_traits=["trait1", "trait2", "trait3"],
    emotional_intelligence=0.9,
    empathy_baseline=0.85,
    background="Character background...",
    speaking_style="How the character speaks...",
    response_patterns={
        "sadness": EmotionalResponsePattern(
            emotion="sadness",
            empathy_level=0.95,
            response_style="deeply empathetic, gentle",
            example_phrases=["Custom phrase 1...", "Custom phrase 2..."]
        ),
        # Add more emotions...
    }
)
```

## ⚙️ Configuration

### Emotion Weight (`emotion_weight`)
Controls how much emotional similarity matters in retrieval:
- `0.0`: Pure semantic similarity (ignore emotions)
- `0.4`: **Default** - Balanced approach
- `0.7`: Heavy emphasis on emotional resonance
- `1.0`: Only retrieve emotionally similar memories

### Retrieval Parameters
```python
# In app/retriever.py
retrieve_context(
    query="user message",
    emotion="detected_emotion",
    top_k=5,              # Number of memories to retrieve
    emotion_weight=0.4,   # Emotion importance
    include_recent=True   # Boost recent memories
)
```

## 📊 How Emotional RAG Works

### Retrieval Scoring Formula

```
combined_score = (1 - emotion_weight) × semantic_score 
                 + emotion_weight × emotion_score 
                 + 0.1 × recency_score
```

Where:
- **Semantic Score**: Embedding cosine similarity (from sentence transformers)
- **Emotion Score**: Emotional similarity (1.0 for same emotion, 0.7 for same group, 0.3 for different)
- **Recency Score**: Exponential decay with 1-hour half-life

### Emotion Groups

Emotions are grouped for similarity scoring:
- **Negative**: sadness, anger, fear, disgust
- **Positive**: joy, happiness, excitement, love
- **Neutral**: surprise, neutral, curiosity

## 📁 Project Structure

```
app/
├── main.py                    # FastAPI app with enhanced endpoints
├── character.py               # Character persona & emotional patterns
├── llm.py                     # Gemini integration with character awareness
├── retriever.py               # Emotion-aware RAG retrieval
├── emotion_detector.py        # Emotion classification
├── conversation_state.py      # Conversation tracking & emotional arc
├── memory.py                  # JSON-based conversation log
└── config.py                  # Configuration & API keys

data/
├── memory.json                # Conversation history
├── conversation_state.json    # Current conversation state
└── embeddings/                # ChromaDB vector storage
    └── chroma.sqlite3
```

## 🧪 Testing the System

### Test Emotional Continuity
```bash
# First message
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message": "I got a promotion today!"}'

# Follow-up (should reference previous joy)
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message": "But now I feel overwhelmed with the new responsibilities"}'
```

### Test Emotion-Weighted Retrieval
```bash
# High emotion weight - prioritize emotional similarity
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message": "I feel anxious", "emotion_weight": 0.8}'

# Low emotion weight - prioritize semantic similarity
curl -X POST http://127.0.0.1:8000/chat \
  -d '{"message": "I feel anxious", "emotion_weight": 0.2}'
```

## 🎯 Best Practices for Human-Like AI

### 1. **Character Consistency**
- Define clear personality traits
- Maintain consistent speaking style
- Use character-specific phrases and vocabulary

### 2. **Emotional Intelligence**
- Validate user emotions ("That's completely understandable")
- Mirror emotional tone appropriately
- Show empathy without being patronizing

### 3. **Context Awareness**
- Reference past conversations naturally
- Track emotional journey
- Acknowledge emotional shifts

### 4. **Natural Responses**
- Vary response length and structure
- Use conversational language
- Ask follow-up questions when appropriate

## 🔧 Advanced Configuration

### Custom Emotion Similarity Function
```python
# In app/retriever.py
def get_emotion_similarity(emotion1: str, emotion2: str) -> float:
    # Add your custom logic here
    # Return 0.0 (no similarity) to 1.0 (identical)
    pass
```

### Adjust Recency Decay
```python
# In retrieve_context(), adjust half-life:
age_hours = age_ms / (1000 * 60 * 60)
recency_score = 0.5 ** (age_hours / 2.0)  # 2-hour half-life instead of 1
```

### Temperature Control
```python
# In generate_reply()
generate_reply(
    context=context,
    user_input=user_input,
    emotion=emotion,
    temperature=0.9,      # Higher = more creative
    max_tokens=800        # Longer responses
)
```

## 🐛 Troubleshooting

### Empty Replies
- Check `GEMINI_API_KEY` is set correctly
- Verify model name in `app/config.py`
- Check terminal logs for API errors

### Poor Retrieval Quality
- Adjust `emotion_weight` parameter
- Increase `top_k` for more context
- Check if memories are being stored correctly

### Character Inconsistency
- Review persona definition in `app/character.py`
- Ensure emotional response patterns are well-defined
- Check prompt construction in `app/llm.py`

## 📝 Future Enhancements

- [ ] Multi-user session management
- [ ] Emotion trajectory prediction
- [ ] Voice/tone analysis integration
- [ ] Long-term memory summarization
- [ ] Personality adaptation over time
- [ ] Multi-modal emotion detection (text + voice)

## 📚 References

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Emotional AI Best Practices](https://www.anthropic.com/index/constitutional-ai-harmlessness-from-ai-feedback)

---

Built with ❤️ for emotionally intelligent AI interactions
