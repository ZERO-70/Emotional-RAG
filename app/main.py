"""Enhanced Emotional RAG API with character consistency and emotional intelligence.

This API provides emotionally-aware conversational AI with:
- Emotion detection and tracking
- Character-consistent personality
- Emotion-weighted memory retrieval
- Conversation state tracking
"""

from fastapi import FastAPI, Body, HTTPException
from typing import Optional
import time

from app.emotion_detector import detect_emotion
from app.retriever import add_to_memory, retrieve_context, get_emotional_context_summary
from app.llm import generate_reply
from app.memory import add_turn
from app.conversation_state import (
    get_conversation_state, 
    add_conversation_turn,
    save_conversation_state
)
from app.character import JAKE_PERSONA, CharacterPersona

app = FastAPI(
    title="Emotional RAG API",
    description="An emotionally intelligent AI companion with RAG-powered memory",
    version="2.0.0"
)


@app.get("/")
def root():
    """API health check and character info."""
    return {
        "status": "online",
        "character": JAKE_PERSONA.name,
        "traits": JAKE_PERSONA.core_traits,
        "emotional_intelligence": f"{JAKE_PERSONA.emotional_intelligence * 100:.0f}%"
    }


@app.post("/chat")
def chat(user_input: dict = Body(...)):
    """
    Main chat endpoint with enhanced emotional RAG.
    
    Expected input:
    {
      "message": "I feel lonely today.",
      "emotion_weight": 0.4,  // optional: how much to weight emotional similarity (0.0-1.0)
      "use_recent_context": true  // optional: include recent conversation history
    }
    
    Returns:
    {
      "reply": "...",
      "user_emotion": "sadness",
      "retrieved_context": [...],
      "emotional_summary": "...",
      "conversation_stats": {...}
    }
    """
    try:
        user_text = user_input.get("message")
        if not user_text:
            raise HTTPException(status_code=400, detail="Message field is required")
        
        # Optional parameters
        emotion_weight = user_input.get("emotion_weight", 0.4)
        use_recent_context = user_input.get("use_recent_context", True)
        
        timestamp = int(time.time() * 1000)

        # 1️⃣ Detect user emotion
        emotion = detect_emotion(user_text)

        print ("[][][][][][][]emotion detected by the model is ", emotion, "[][][][]][]")

        # 2️⃣ Get conversation state for context
        conv_state = get_conversation_state()
        recent_history = conv_state.get_recent_context(n=3) if use_recent_context else None

        # 3️⃣ Retrieve emotional context with enhanced strategy
        context_docs = retrieve_context(
            query=user_text,
            emotion=emotion,
            top_k=5,
            emotion_weight=emotion_weight,
            include_recent=True
        )
        context = "\n---\n".join(context_docs) if context_docs else ""

        # 4️⃣ Generate AI reply with character consistency
        reply = generate_reply(
            context=context,
            user_input=user_text,
            emotion=emotion,
            persona=JAKE_PERSONA,
            conversation_history=recent_history
        )

        # 5️⃣ Store in memory systems
        add_to_memory(user_text, emotion, speaker="user", bot_reply=reply)
        add_turn(user_text, emotion, reply)
        add_conversation_turn(user_text, emotion, reply, timestamp)

        # 6️⃣ Get emotional insights
        emotional_summary = get_emotional_context_summary(emotion, top_k=3)
        conv_state = get_conversation_state()  # Refresh after adding turn

        return {
            "reply": reply,
            "user_emotion": emotion,
            "retrieved_context": context_docs,
            "emotional_summary": emotional_summary,
            "conversation_stats": {
                "turn_count": len(conv_state.turns),
                "dominant_emotion": conv_state.dominant_emotion,
                "emotional_journey": " → ".join(conv_state.emotion_history[-5:]) if conv_state.emotion_history else "Starting conversation"
            },
            "character": JAKE_PERSONA.name
        }
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/conversation/state")
def get_state():
    """Get current conversation state and emotional arc."""
    state = get_conversation_state()
    return {
        "turn_count": len(state.turns),
        "dominant_emotion": state.dominant_emotion,
        "emotion_history": state.emotion_history,
        "emotional_summary": state.get_emotional_summary(),
        "recent_context": state.get_recent_context(n=5)
    }


@app.post("/conversation/reset")
def reset_conversation():
    """Reset conversation state (useful for starting fresh)."""
    from app.conversation_state import ConversationState, STATE_FILE
    import app.conversation_state as conv_module
    
    # Create new empty state
    new_state = ConversationState()
    conv_module._conversation_state = new_state
    save_conversation_state(new_state)
    
    # Optionally clear state file
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    
    return {"status": "conversation reset", "message": "Starting fresh with clean emotional slate"}


@app.get("/character")
def get_character_info():
    """Get detailed information about the AI character."""
    persona = JAKE_PERSONA
    return {
        "name": persona.name,
        "traits": persona.core_traits,
        "emotional_intelligence": persona.emotional_intelligence,
        "empathy_baseline": persona.empathy_baseline,
        "background": persona.background,
        "speaking_style": persona.speaking_style,
        "response_patterns": {
            emotion: {
                "empathy_level": pattern.empathy_level,
                "response_style": pattern.response_style,
                "example_phrases": pattern.example_phrases
            }
            for emotion, pattern in persona.response_patterns.items()
        }
    }
