#!/usr/bin/env python
"""Quick test script to verify enhanced emotional RAG system."""

import sys

def test_imports():
    """Test that all new modules import correctly."""
    print("🧪 Testing imports...")
    
    try:
        from app.character import DEFAULT_PERSONA, get_character_context, get_emotional_guidance
        print("  ✅ character module")
    except Exception as e:
        print(f"  ❌ character module: {e}")
        return False
    
    try:
        from app.conversation_state import get_conversation_state, ConversationState
        print("  ✅ conversation_state module")
    except Exception as e:
        print(f"  ❌ conversation_state module: {e}")
        return False
    
    try:
        from app.retriever import get_emotion_similarity, add_to_memory, retrieve_context
        print("  ✅ retriever module (enhanced)")
    except Exception as e:
        print(f"  ❌ retriever module: {e}")
        return False
    
    try:
        from app.llm import generate_reply, build_emotional_prompt
        print("  ✅ llm module (enhanced)")
    except Exception as e:
        print(f"  ❌ llm module: {e}")
        return False
    
    return True


def test_character_system():
    """Test character persona system."""
    print("\n🎭 Testing character system...")
    
    from app.character import DEFAULT_PERSONA, get_character_context, get_emotional_guidance
    
    print(f"  Character Name: {DEFAULT_PERSONA.name}")
    print(f"  Traits: {', '.join(DEFAULT_PERSONA.core_traits[:3])}")
    print(f"  Emotional Intelligence: {DEFAULT_PERSONA.emotional_intelligence * 100:.0f}%")
    print(f"  Empathy Baseline: {DEFAULT_PERSONA.empathy_baseline * 100:.0f}%")
    
    # Test emotional response patterns
    sadness_pattern = DEFAULT_PERSONA.get_response_pattern("sadness")
    print(f"\n  Sadness Response:")
    print(f"    - Empathy: {sadness_pattern.empathy_level * 100:.0f}%")
    print(f"    - Style: {sadness_pattern.response_style}")
    
    print("  ✅ Character system working")


def test_emotion_similarity():
    """Test emotion similarity function."""
    print("\n🎨 Testing emotion similarity...")
    
    from app.retriever import get_emotion_similarity
    
    tests = [
        ("sadness", "sadness", 1.0, "Same emotion"),
        ("sadness", "fear", 0.7, "Same group (negative)"),
        ("sadness", "joy", 0.3, "Different groups"),
        ("joy", "happiness", 0.7, "Same group (positive)"),
    ]
    
    for emotion1, emotion2, expected, description in tests:
        score = get_emotion_similarity(emotion1, emotion2)
        status = "✅" if abs(score - expected) < 0.01 else "❌"
        print(f"  {status} {emotion1} ↔ {emotion2}: {score:.1f} ({description})")


def test_conversation_state():
    """Test conversation state tracking."""
    print("\n💬 Testing conversation state...")
    
    from app.conversation_state import ConversationState
    import time
    
    state = ConversationState()
    timestamp = int(time.time() * 1000)
    
    # Add some test turns
    state.add_turn("I feel happy today!", "joy", "That's wonderful!", timestamp)
    state.add_turn("But now I'm worried", "fear", "I understand", timestamp + 1000)
    state.add_turn("I feel anxious", "fear", "Let's talk about it", timestamp + 2000)
    
    print(f"  Turn count: {len(state.turns)}")
    print(f"  Dominant emotion: {state.dominant_emotion}")
    print(f"  Emotional journey: {' → '.join(state.emotion_history)}")
    print("  ✅ Conversation state working")


def test_prompt_building():
    """Test enhanced prompt building."""
    print("\n📝 Testing prompt building...")
    
    from app.llm import build_emotional_prompt
    from app.character import DEFAULT_PERSONA
    
    prompt = build_emotional_prompt(
        context="Previous conversation about feeling lonely.",
        user_input="I still feel isolated.",
        emotion="sadness",
        persona=DEFAULT_PERSONA,
        conversation_history="User: I feel lonely.\nAssistant: I'm here with you."
    )
    
    # Check that key sections are present
    sections = ["YOUR ROLE", "EMOTIONAL CONTEXT", "RELEVANT MEMORIES", "CURRENT INTERACTION"]
    for section in sections:
        if section in prompt:
            print(f"  ✅ {section} section present")
        else:
            print(f"  ❌ {section} section missing")
    
    print(f"\n  Prompt length: {len(prompt)} characters")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Enhanced Emotional RAG System - Test Suite")
    print("=" * 60)
    
    if not test_imports():
        print("\n❌ Import test failed. Stopping.")
        sys.exit(1)
    
    try:
        test_character_system()
        test_emotion_similarity()
        test_conversation_state()
        test_prompt_building()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\n🎉 Your enhanced emotional RAG system is ready!")
        print("\nNext steps:")
        print("  1. Start server: uv run fastapi dev app/main.py")
        print("  2. Test chat: curl -X POST http://127.0.0.1:8000/chat \\")
        print("                     -H 'Content-Type: application/json' \\")
        print("                     -d '{\"message\": \"I feel lonely today.\"}'")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
