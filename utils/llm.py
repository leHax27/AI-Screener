import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)

def call_llm(prompt: str, system_instruction: str = None, json_mode: bool = False, retries: int = 3) -> str:
    last_exception = None
    
    # We must wrap system_instruction and json_mode inside a GenerateContentConfig object
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json" if json_mode else "text/plain"
    )

    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=config  # This now contains both the persona and the JSON setting
            )
            return response.text

        except Exception as e:
            last_exception = e
            print(f"[LLM WARNING] Attempt {attempt} failed: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError(f"LLM failed after {retries} attempts: {last_exception}")