import json
import re

def extract_json(text: str) -> dict:
    """
    Extracts JSON from LLM response, handling markdown blocks and stray text.
    """
    # Remove markdown code blocks
    text = re.sub(r"```json\s?|\s?```", "", text).strip()
    
    # Try direct load
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # If it fails, try to find the first '{' and last '}'
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
            except:
                return {"error": "Deep JSON parsing failed"}
        else:
            return {"error": "No JSON found in response"}

    # Flatten list to dict if necessary
    if isinstance(data, list):
        return data[0] if len(data) > 0 else {}
    
    return data