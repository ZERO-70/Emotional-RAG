"""Conversation state tracking for emotional continuity and context awareness.

This module maintains the emotional arc of the conversation and provides
contextual information for more coherent, human-like responses.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import deque
import json
from pathlib import Path


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    user_message: str
    user_emotion: str
    bot_response: str
    timestamp: int
    

@dataclass
class ConversationState:
    """Tracks the current state and emotional arc of the conversation."""
    turns: deque = field(default_factory=lambda: deque(maxlen=10))  # Keep last 10 turns
    dominant_emotion: str = "neutral"
    emotion_history: List[str] = field(default_factory=list)
    
    def add_turn(self, user_msg: str, emotion: str, bot_reply: str, timestamp: int):
        """Add a new conversation turn."""
        turn = ConversationTurn(user_msg, emotion, bot_reply, timestamp)
        self.turns.append(turn)
        self.emotion_history.append(emotion)
        self._update_dominant_emotion()
    
    def _update_dominant_emotion(self):
        """Update the dominant emotion based on recent history."""
        if not self.emotion_history:
            self.dominant_emotion = "neutral"
            return
        
        # Look at last 5 emotions
        recent = self.emotion_history[-5:]
        emotion_counts = {}
        for emotion in recent:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Most common recent emotion
        self.dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    
    def get_recent_context(self, n: int = 3) -> str:
        """Get formatted recent conversation history."""
        if not self.turns:
            return ""
        
        recent_turns = list(self.turns)[-n:]
        context_lines = []
        
        for turn in recent_turns:
            context_lines.append(f"User ({turn.user_emotion}): {turn.user_message}")
            context_lines.append(f"Assistant: {turn.bot_response}")
        
        return "\n".join(context_lines)
    
    def get_emotional_summary(self) -> str:
        """Get a summary of the emotional journey."""
        if not self.emotion_history:
            return "Beginning of conversation"
        
        recent_emotions = self.emotion_history[-5:]
        emotion_sequence = " → ".join(recent_emotions)
        
        return f"Emotional journey: {emotion_sequence}\nCurrent dominant emotion: {self.dominant_emotion}"
    
    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "turns": [
                {
                    "user_message": t.user_message,
                    "user_emotion": t.user_emotion,
                    "bot_response": t.bot_response,
                    "timestamp": t.timestamp
                }
                for t in self.turns
            ],
            "dominant_emotion": self.dominant_emotion,
            "emotion_history": self.emotion_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConversationState":
        """Deserialize state from dictionary."""
        state = cls()
        state.dominant_emotion = data.get("dominant_emotion", "neutral")
        state.emotion_history = data.get("emotion_history", [])
        
        turns_data = data.get("turns", [])
        for turn_data in turns_data:
            turn = ConversationTurn(
                user_message=turn_data["user_message"],
                user_emotion=turn_data["user_emotion"],
                bot_response=turn_data["bot_response"],
                timestamp=turn_data["timestamp"]
            )
            state.turns.append(turn)
        
        return state


# Global conversation state (in production, use session-based storage)
_conversation_state = ConversationState()
STATE_FILE = Path("data/conversation_state.json")


def get_conversation_state() -> ConversationState:
    """Get the current conversation state."""
    global _conversation_state
    
    # Load from disk if available
    if _conversation_state.turns.__len__() == 0 and STATE_FILE.exists():
        try:
            content = STATE_FILE.read_text().strip()
            if content:
                data = json.loads(content)
                _conversation_state = ConversationState.from_dict(data)
        except Exception as e:
            print(f"Failed to load conversation state: {e}")
    
    return _conversation_state


def save_conversation_state(state: ConversationState):
    """Persist conversation state to disk."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state.to_dict(), indent=2))
    except Exception as e:
        print(f"Failed to save conversation state: {e}")


def add_conversation_turn(user_msg: str, emotion: str, bot_reply: str, timestamp: int):
    """Add a turn to the conversation state and save it."""
    state = get_conversation_state()
    state.add_turn(user_msg, emotion, bot_reply, timestamp)
    save_conversation_state(state)
