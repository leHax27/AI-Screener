from utils.llm import call_llm
from utils.json_utils import extract_json
from utils.pdf_reader import extract_text_from_pdf

class ResumeParserAgent:
    def __init__(self):
        self.system_instruction = (
            "You are an expert Resume Parser. Your job is to extract structured data "
            "from raw resume text. Focus heavily on 'technical_skills' and 'work_experience'."
        )

    def run(self, source: str, is_path: bool = True) -> dict:
        # 1. Extract Text
        try:
            if is_path:
                text = extract_text_from_pdf(source)
            else:
                text = source
            
            if not text or len(text) < 50:
                print("❌ [RESUME PARSER] Text extraction too short/empty.")
                return {"error": "Empty resume text"}
                
        except Exception as e:
            print(f"❌ [RESUME PARSER] PDF Read Error: {e}")
            return {"error": f"PDF Error: {str(e)}"}

        # 2. LLM Parsing
        prompt = f"""
EXTRACT DATA FROM RESUME.
Resume Text:
{text[:6000]}

OUTPUT SCHEMA (JSON):
{{
  "personal_information": {{ "name": "string", "email": "string" }},
  "technical_skills": ["list", "of", "skills"],
  "work_experience": [ {{ "role": "string", "company": "string", "description": "string" }} ],
  "education": [ {{ "degree": "string", "institution": "string" }} ],
  "total_years_experience": float
}}
"""
        # Attempt 1
        response = call_llm(prompt, system_instruction=self.system_instruction, json_mode=True)
        
        try:
            parsed = extract_json(response)
            if self._validate(parsed):
                return parsed
        except Exception as e:
            print(f"⚠️ [RESUME PARSER] Attempt 1 failed: {e}")

        # Attempt 2 (Retry with simplified prompt if first failed)
        print("🔄 [RESUME PARSER] Retrying with stricter prompt...")
        return self._retry_parsing(text)

    def _retry_parsing(self, text):
        prompt = f"""
You failed to parse the resume previously. 
Extract ONLY these two keys in strict JSON:
{{
  "technical_skills": ["skill1", "skill2"],
  "work_experience": []
}}
Resume: {text[:4000]}
"""
        response = call_llm(prompt, system_instruction=self.system_instruction, json_mode=True)
        try:
            return extract_json(response)
        except:
            return {"error": "Failed to parse resume after retries"}

    def _validate(self, data: dict) -> bool:
        """Greedy Validation: As long as we have skills or experience, it's good."""
        if not isinstance(data, dict): return False
        
        has_skills = "technical_skills" in data and len(data["technical_skills"]) > 0
        has_exp = "work_experience" in data and len(data["work_experience"]) > 0
        
        # If we have EITHER skills OR experience, we can work with it.
        return has_skills or has_exp