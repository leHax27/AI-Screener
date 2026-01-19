import os
import time
import json
from agents.resume_parser import ResumeParserAgent
from agents.jd_analyzer import JDAnalyzerAgent
from agents.decision_agent import DecisionAgent

def main():
    # Initialize agents
    resume_agent = ResumeParserAgent()
    jd_agent = JDAnalyzerAgent()
    decision_agent = DecisionAgent()

    # Define directories
    jd_dir = "data/job_descriptions"
    resume_dir = "data/resumes"
    output_dir = "data/sample_outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Get file lists
    jd_files = [f for f in os.listdir(jd_dir) if f.endswith(".txt")]
    resume_files = [f for f in os.listdir(resume_dir) if f.endswith(".pdf")]

    if not jd_files or not resume_files:
        print("Missing input files. Ensure PDFs are in 'resumes' and TXTs in 'job_descriptions'.")
        return

    print(f"🚀 Starting Screening: {len(resume_files)} Resumes x {len(jd_files)} JDs")

    for jd_file in jd_files:
        # 1. Analyze JD once (saves API calls)
        jd_path = os.path.join(jd_dir, jd_file)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
        
        print(f"\n[PHASE 1] Analyzing Job Description: {jd_file}")
        jd_requirements = jd_agent.run(jd_text)
        time.sleep(2) # Breathing room for API

        for resume_file in resume_files:
            print(f"  └─ Evaluating Resume: {resume_file}...")
            resume_path = os.path.join(resume_dir, resume_file)

            try:
                # 2. Extract Resume Data
                resume_data = resume_agent.run(resume_path, is_path=True)
                time.sleep(2)

                # 3. Agentic Decision Making
                final_result = decision_agent.run(resume_data, jd_requirements)

                # 4. Display Results in Requested Format
                print("\n--- EVALUATION RESULT ---")
                print(json.dumps(final_result, indent=2))
                
                # 5. Save to output folder (Bonus for Documentation!)
                output_filename = f"result_{resume_file.split('.')[0]}_{jd_file.split('.')[0]}.json"
                with open(os.path.join(output_dir, output_filename), "w") as out:
                    json.dump(final_result, out, indent=2)

            except Exception as e:
                print(f"      ❌ Failed to evaluate {resume_file}: {e}")
            
            # Batching pause to avoid 429 Resource Exhausted
            print("  [Waiting 10s for next evaluation...]")
            time.sleep(10)

if __name__ == "__main__":
    main()