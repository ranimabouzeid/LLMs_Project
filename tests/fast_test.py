from pipeline.teaching_pipeline import pipeline
from agents.retrieval_judge import RetrievalJudge

def run_fast_test():
    print("🚀 Running FAST Pipeline Test (Skipping Judge)...")
    
    # Temporarily lower the judge threshold so it accepts everything immediately
    pipeline.judge.threshold = -1.0 
    
    student_query = "Explain Linear Regression in 2 sentences."
    result = pipeline.run_pipeline(student_query)
    
    print("\n✅ Fast Test Complete!")
    print(result["explanation"][:200] + "...")

if __name__ == "__main__":
    run_fast_test()
