🤖 Agentic Resume Screener
A multi-agent AI system that automates the initial screening of technical candidates. Unlike simple keyword matchers, this system uses a Specialist Committee architecture to semantically evaluate candidates, handling ambiguous job descriptions and preventing common LLM hallucinations.

🏗️ Architecture: The Specialist Committee
This project moves beyond a linear data pipeline. It employs three distinct AI Agents acting as a hiring committee:

ResumeParserAgent ("The Scribe"):

Extracts structured entities (Skills, Experience, Education) from raw PDF text.

Agentic Feature: Implements a "Greedy Validation" loop. If the initial parse fails (e.g., weird formatting), it self-corrects with a simplified extraction prompt rather than crashing.

JDAnalyzerAgent ("The Strategist"):

Analyzes Job Descriptions to distinguish between Mandatory vs. Nice-to-Have skills.

Agentic Feature: Uses a "Schema-Agnostic" extraction method to handle unstructured JDs (e.g., JDs that list "Programming knowledge" instead of specific languages).

DecisionAgent ("The Hiring Manager"):

Synthesizes data from the previous two agents to make a hiring recommendation.

Agentic Feature: Features a Semantic Bridge and Anti-Hallucination Guardrails (detailed below).

🚀 Key Technical Features
1. Semantic Ambiguity Handling
Standard keyword matchers fail when a JD asks for "Database experience" but the resume lists "PostgreSQL."

Solution: I implemented a Semantic Bridge Prompt in the DecisionAgent. It maps generic requirements (e.g., "Fintech domain") to specific evidence in the resume (e.g., "Experience with Stripe/Razorpay"), ensuring qualified candidates aren't rejected due to vocabulary mismatches.

2. X-Ray Debugging Layer
Deeply nested JSON structures from LLMs often lead to data loss.

Solution: A custom recursive search algorithm (_smart_get_skills) acts as an "X-Ray," flattening nested dictionaries (like technical_skills: { languages: [...], tools: [...] }) into a single comparison plane. This ensures the Decision Agent always sees the full picture.

3. Anti-Hallucination & Grounding
LLMs have a known bias toward common stacks (e.g., assuming "Backend" implies "Java").

Solution: The system uses Strict Grounding Protocols. The Decision Agent is forbidden from inferring skills not explicitly present in the data. It uses a "Truth List" derived strictly from the JD to validate matches, preventing false positives based on the model's training data.

🛠️ Setup & Usage
Prerequisites
Python 3.9+

Google Gemini API Key

Installation
Clone the repository:

Bash
git clone https://github.com/your-username/agentic-resume-screener.git
cd agentic-resume-screener
Install dependencies:

Bash
pip install -r requirements.txt
Configure Environment: Create a .env file in the root directory:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key_here
Running the Screener
Place your data in the respective folders:

Resumes: data/resumes/*.pdf

Job Descriptions: data/job_descriptions/*.txt

Run the main script:

Bash
python main.py
Results will be saved as JSON files in data/sample_outputs/


🔮 Future Improvements
Pydantic Output Parsers: To enforce strict typing on agent outputs, replacing the current "Defensive Flattening" logic.

Human-in-the-Loop UI: A Streamlit dashboard to allow recruiters to override specific agent decisions and retrain the prompts.