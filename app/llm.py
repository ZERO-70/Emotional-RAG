"""LLM integration using Google Gemini API with character-aware emotional intelligence.

This module uses the google-generativeai library to generate responses
from Gemini models with consistent character personality and emotional awareness.
"""

from typing import Any, Optional
import google.generativeai as genai
from app.config import GEMINI_API_KEY, MODEL_NAME
from app.character import (
    JAKE_PERSONA,
    CharacterPersona, 
    DEFAULT_PERSONA, 
    get_character_context,
    get_emotional_guidance
)


def build_emotional_prompt(
    context: str,
    user_input: str,
    emotion: str,
    persona: CharacterPersona = JAKE_PERSONA,
    conversation_history: Optional[str] = None
) -> str:
    """Build a comprehensive prompt with character and emotional awareness.
    
    Args:
        context: Retrieved relevant memories/context
        user_input: Current user message
        emotion: Detected emotion
        persona: Character persona to use
        conversation_history: Recent conversation turns (optional)
    
    Returns:
        Formatted prompt string
    """
    character_info = get_character_context(persona)
    emotional_guide = get_emotional_guidance(emotion, persona)
    
    prompt_parts = [
        "# YOUR ROLE",
        character_info,
        "",
        "# EMOTIONAL CONTEXT",
        f"The user is currently experiencing: **{emotion}**",
        "",
        emotional_guide,
        "",
        "# RELEVANT MEMORIES & CONTEXT",
        "Here are relevant past moments from our conversation:",
        context if context.strip() else "(No relevant history yet - this may be our first interaction)",
        "",
    ]
    
    if conversation_history:
        prompt_parts.extend([
            "# RECENT CONVERSATION",
            conversation_history,
            "",
        ])
    
    prompt_parts.extend([
        "# CURRENT INTERACTION",
        f"User: {user_input}",
        "",
        "# YOUR RESPONSE",
        f"Respond as {persona.name}, maintaining your character traits and responding appropriately to the user's {emotion}.",
        "Be authentic, empathetic, and true to your personality. Keep your response natural and conversational.",
        "",
        f"{persona.name}:"
    ])
    
    return "\n".join(prompt_parts)


def generate_reply(
    context: str, 
    user_input: str, 
    emotion: str,
    persona: CharacterPersona = DEFAULT_PERSONA,
    conversation_history: Optional[str] = None,
    temperature: float = 0.8,
    max_tokens: int = 1500
) -> str:
    """Generate an emotionally-aware reply with character consistency.

    Args:
        context: Retrieved context from memory/RAG
        user_input: User's message
        emotion: Detected emotion label
        persona: Character persona to maintain
        conversation_history: Recent conversation for continuity
        temperature: Sampling temperature (0.0-1.0, higher = more creative)
        max_tokens: Maximum response length

    Returns:
        Generated reply string, or empty string on error
    """
    prompt = build_emotional_prompt(
        context=context,
        user_input=user_input,
        emotion=emotion,
        persona=persona,
        conversation_history=conversation_history
    )
    
    # Debug: Log prompt stats
    print(f"[llm.generate_reply] Prompt length: {len(prompt)} chars, ~{len(prompt.split())} words")
    if len(prompt) > 10000:
        print(f"[llm.generate_reply] WARNING: Very long prompt, may cause issues")

    try:
        # Use the simple GenerativeModel interface
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Configure generation parameters - increase max tokens significantly
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        # Configure safety settings to be more permissive for emotional conversations
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        print(f"[llm.generate_reply] Calling API with max_tokens={max_tokens}, temp={temperature}")
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Debug: Log the full response structure
        print(f"[llm.generate_reply] Response received")
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            print(f"[llm.generate_reply] Candidate finish_reason: {candidate.finish_reason}")
            if hasattr(candidate, 'safety_ratings'):
                print(f"[llm.generate_reply] Safety ratings: {candidate.safety_ratings}")
        
        # Check for blocked response first
        if hasattr(response, 'prompt_feedback'):
            print(f"[llm.generate_reply] Prompt feedback: {response.prompt_feedback}")
            if hasattr(response.prompt_feedback, 'block_reason'):
                block_reason = response.prompt_feedback.block_reason
                if block_reason:
                    print(f"[llm.generate_reply] Prompt blocked: {block_reason}")
                    return "I want to respond thoughtfully to what you've shared. Could you tell me more in a different way?"
        
        # Check candidate finish_reason
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            # Check finish_reason (using the enum value directly)
            if hasattr(candidate, 'finish_reason'):
                finish_reason = int(candidate.finish_reason)
                print(f"[llm.generate_reply] finish_reason numeric: {finish_reason}")
                
                # FinishReason enum: FINISH_REASON_UNSPECIFIED=0, STOP=1, MAX_TOKENS=2, 
                #                    SAFETY=3, RECITATION=4, OTHER=5
                if finish_reason == 3:  # SAFETY
                    print(f"[llm.generate_reply] Response blocked by safety filters")
                    return "I hear what you're sharing. Let me respond in a supportive way - could you share more about what you're feeling right now?"
                elif finish_reason == 2:  # MAX_TOKENS
                    print(f"[llm.generate_reply] Response hit max tokens - trying to extract partial text")
                    # Continue to try extraction for partial response
                elif finish_reason == 4:  # RECITATION
                    print(f"[llm.generate_reply] Response blocked due to recitation")
                    return "I'd like to give you an original, thoughtful response. Could you rephrase what you shared?"
                elif finish_reason not in [1, 2]:  # Not STOP or MAX_TOKENS
                    print(f"[llm.generate_reply] Unexpected finish_reason: {finish_reason}")
        
        # Extract text from response - defensive approach
        try:
            # Try the quick accessor first
            text = response.text
            if text:
                return text.strip()
        except (ValueError, AttributeError) as e:
            # response.text raised an error, try manual extraction
            print(f"[llm.generate_reply] response.text accessor failed: {e}")
        
        # Manual extraction from candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            print(f"[llm.generate_reply] Attempting manual extraction from candidate")
            
            if hasattr(candidate, 'content'):
                content = candidate.content
                print(f"[llm.generate_reply] Content type: {type(content)}")
                print(f"[llm.generate_reply] Content: {content}")
                
                if hasattr(content, 'parts'):
                    parts = content.parts
                    print(f"[llm.generate_reply] Parts type: {type(parts)}, length: {len(parts) if parts else 0}")
                    
                    if parts and len(parts) > 0:
                        print(f"[llm.generate_reply] Parts count: {len(parts)}")
                        # Collect text from all parts
                        text_parts = []
                        for i, part in enumerate(parts):
                            print(f"[llm.generate_reply] Part {i}: {type(part)}, {part}")
                            if hasattr(part, 'text'):
                                part_text = part.text
                                if part_text:
                                    print(f"[llm.generate_reply] Part {i} text length: {len(part_text)}")
                                    text_parts.append(part_text)
                            else:
                                print(f"[llm.generate_reply] Part {i} has no text attribute")
                        
                        if text_parts:
                            result = " ".join(text_parts).strip()
                            print(f"[llm.generate_reply] Successfully extracted {len(result)} chars")
                            return result
                    else:
                        print(f"[llm.generate_reply] Parts is None or empty: {parts}")
                else:
                    print(f"[llm.generate_reply] Content has no parts attribute")
            else:
                print(f"[llm.generate_reply] Candidate has no content")
        
        print(f"[llm.generate_reply] No valid text in response. Type: {type(response)}")
        if hasattr(response, 'candidates'):
            print(f"[llm.generate_reply] Candidates: {len(response.candidates) if response.candidates else 0}")
        
        # Last resort - check if this is truly empty or just blocked
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason') and int(candidate.finish_reason) == 3:
                return "I'm here to listen and support you. Sometimes I need you to express things a bit differently so I can respond properly. What's most important for you to share right now?"
        
        return "I'm here to support you. Could you tell me more about what you're experiencing?"
        
    except Exception as e:
        print(f"[llm.generate_reply] error calling model: {e}")
        import traceback
        traceback.print_exc()
        return "I'm experiencing a technical difficulty, but I'm still here for you. Let's try continuing our conversation."
