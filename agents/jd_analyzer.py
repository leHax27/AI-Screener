from utils.llm import call_llm
from utils.json_utils import extract_json
# Remove strict schema import if it causes issues, or keep for optional checking
from utils.schemas import JD_SCHEMA
from utils.validator import validate_schema

class JDAnalyzerAgent:
    def __init__(self):
        self.system_instruction = (
            "You are an expert Technical Recruiter. Extract requirements strictly."
        )

    def run(self, jd_text: str) -> dict:
        prompt = f"""
Analyze the Job Description.
STEP 1: Extract 'required_skills' (Must-haves) as a list of strings.
STEP 2: Extract 'preferred_skills' (Nice-to-haves) as a list of strings.
STEP 3: Extract 'seniority' (Junior/Mid/Senior/Unknown).

JD: {jd_text[:4000]}

Return STRICT JSON.
"""
        response = call_llm(
            prompt, 
            system_instruction=self.system_instruction, 
            json_mode=True
        )

        try:
            parsed = extract_json(response)
            
            # 🚨 GREEDY FIX: If we have skills, TAKE IT. Ignore strict schema validation.
            if "required_skills" in parsed and isinstance(parsed["required_skills"], list):
                return parsed
            
            # Fallback to schema check only if "required_skills" is missing
            if validate_schema(parsed, JD_SCHEMA):
                return parsed
                
        except Exception as e:
            # Silent failure logic here if needed, or just proceed to retry
            pass

        # Only retry if we truly have nothing
        return self._retry_analysis(jd_text)

    def _retry_analysis(self, jd_text):
        retry_prompt = "Extract ONLY: {'required_skills': ['...']}. Do not add other keys."
        response = call_llm(retry_prompt, system_instruction=self.system_instruction, json_mode=True)
        try:
            return extract_json(response)
        except:
            return {"required_skills": [], "error": "Retry failed"}