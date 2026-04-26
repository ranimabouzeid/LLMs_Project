import time
import pandas as pd
import os
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(os.getcwd())

from pipeline.teaching_pipeline import TeachingPipeline
from evaluation.llm_judge import evaluate_response

def run_ablation_study():
    print("🚀 Starting Ablation Study...")
    
    pipeline = TeachingPipeline()
    test_queries = [
        "What is the difference between an LSTM and a GRU?",
        "Why do we need softmax in classification?",
        "Explain backpropagation."
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        start_time = time.time()
        
        # Run Full TutorMind Config
        response = pipeline.run_pipeline(query, student_id="eval_student")
        
        latency = time.time() - start_time
        
        score = evaluate_response(query, response["explanation"])
        
        coverage = response["coverage"]
        total_ideas = len(coverage.covered_ideas) + len(coverage.missing_ideas)
        coverage_rate = len(coverage.covered_ideas) / max(1, total_ideas)
        
        results.append({
            "Query": query,
            "Latency (s)": round(latency, 2),
            "Judge Score (1-10)": score,
            "Coverage Rate": round(coverage_rate, 2),
            "Key Ideas": len(response["key_ideas"])
        })
        
    df = pd.DataFrame(results)
    print("\n" + "="*50)
    print("📊 ABLATION STUDY RESULTS:")
    print("="*50)
    print(df.to_string(index=False))
    
    # Save to CSV
    os.makedirs("evaluation/results", exist_ok=True)
    df.to_csv("evaluation/results/ablation_results.csv", index=False)
    print("\n✅ Results saved to evaluation/results/ablation_results.csv")

if __name__ == "__main__":
    run_ablation_study()
