import google.generativeai as genai
import os

# Add your API key here or load from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBT_BKhMb4Cshgs4vIyH_71N6GoYaDg9t0")
genai.configure(api_key=GEMINI_API_KEY)

# You can use this globally later
MODEL_NAME = "gemini-2.5-flash"
