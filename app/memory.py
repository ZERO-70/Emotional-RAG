import json
from pathlib import Path

MEMORY_FILE = Path("data/memory.json")

def load_memory():
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text().strip()
        if content:
            return json.loads(content)
    return []

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

def add_turn(user_text: str, user_emotion: str, bot_reply: str):
    memory = load_memory()
    memory.append({
        "user_text": user_text,
        "user_emotion": user_emotion,
        "bot_reply": bot_reply
    })
    save_memory(memory)
