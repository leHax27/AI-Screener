from utils.llm import call_llm
from utils.json_utils import extract_json

class DecisionAgent:
    def __init__(self):
        self.system_instruction = (
            "You are a strict Data Comparison Engine. You verify matches between "
            "two provided lists. You DO NOT infer missing skills. You DO NOT "
            "suggest adjacent roles (like Data Science) if they are not requested."
        )

    def _flatten_skills(self, data):
        """Helper to flatten nested dictionaries (like 'technical_skills') into a single list."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Aggressively grab every list inside the dict
            all_skills = []
            for key, val in data.items():
                if isinstance(val, list):
                    all_skills.extend(val)
            return all_skills
        return []

    def _smart_get_skills(self, data: dict, source_name: str) -> list:
        target_data = []

        # 1. Prioritize 'technical_skills' (The Resume Standard)
        if "technical_skills" in data:
            target_data = self._flatten_skills(data["technical_skills"])
        
        # 2. Check for 'required_skills' (The JD Standard)
        elif "required_skills" in data:
            target_data = data["required_skills"]
            
        # 3. Check for generic 'skills'
        elif "skills" in data:
            target_data = self._flatten_skills(data["skills"])

        # 4. Fallback: Search for any list containing "Python" or "SQL" (Heuristic)
        else:
            for val in data.values():
                if isinstance(val, list) and len(val) > 0:
                    # check if it looks like skills (strings) not objects
                    if isinstance(val[0], str): 
                        target_data = val
                        break
        
        if not target_data:
            return []
            
        return target_data

    def run(self, resume_data: dict, jd_data: dict) -> dict:
        # Sanitize Inputs
        if isinstance(resume_data, list): resume_data = resume_data[0] if resume_data else {}
        if isinstance(jd_data, list): jd_data = jd_data[0] if jd_data else {}
        
        # Extract Skills
        jd_skills = self._smart_get_skills(jd_data, "JOB DATA")
        cand_skills = self._smart_get_skills(resume_data, "RESUME DATA")

        prompt = f"""
SEMANTIC MATCHING TASK:
You are an expert evaluator who understands that Job Descriptions often use generic terms.

JOB REQUIREMENTS: {jd_skills}
CANDIDATE SKILLS: {cand_skills}

INSTRUCTIONS:
1. DIRECT MATCH: If JD says "Python" and Candidate has "Python" -> MATCH.
2. CATEGORY MATCH: 
   - If JD says "Programming knowledge" or "Coding skills" AND Candidate has ANY language (Python, Java, JS) -> MATCH.
   - If JD says "Database experience" AND Candidate has SQL, PostgreSQL, Mongo -> MATCH.
   - If JD says "Framework experience" AND Candidate has Django, React, Spring -> MATCH.
3. DOMAIN MATCH:
   - "Fintech" matches "Razorpay", "Stripe", "Payments".
   - "Cloud" matches "AWS", "Azure", "GCP".

CALCULATE SCORE:
- Match Score should be high (0.8+) if the candidate fulfills the *intent* of the requirements, even if exact words differ.

Return JSON:
{{
  "match_score": float,
  "recommendation": "string",
  "requires_human": bool,
  "confidence": float,
  "reasoning_summary": "string"
}}
"""
        response = call_llm(prompt, system_instruction=self.system_instruction, json_mode=True)
        
        try:
            return extract_json(response)
        except Exception as e:
            return {"match_score": 0.0, "reasoning_summary": f"Error: {e}"}