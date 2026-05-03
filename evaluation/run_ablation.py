import asyncio
import time
import pandas as pd
import os
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(os.getcwd())

from pipeline.teaching_pipeline import TeachingPipeline, AblationConfig
from evaluation.llm_judge import evaluate_response
from memory.db_init import init_db

async def run_ablation_study():
    # Ensure database is initialized before starting
    init_db()
    
    print("🚀 [Evaluation] Starting Multi-Config Ablation Study...")
    print("⚠️  QUOTA GUARD: 12s sleep between questions to stay under 5 RPM.")
    print("❄️  CACHE DISABLED: Measuring raw cold-start performance for report accuracy.")
    
    pipeline = TeachingPipeline()
    test_queries = [
        "What is the difference between an LSTM and a GRU?",
        "Why do we need softmax in classification?",
        "Explain backpropagation."
    ]
    
    # Define the 4 configurations (Force use_cache=False for all)
    configs = {
        "A: Baseline": AblationConfig(use_tarj=False, use_ecv=False, use_cdl=False, use_domain_adaptation=False, use_cache=False),
        "B: +TARJ+ECV": AblationConfig(use_tarj=True, use_ecv=True, use_cdl=False, use_domain_adaptation=False, use_cache=False),
        "C: +CDL": AblationConfig(use_tarj=True, use_ecv=True, use_cdl=True, use_domain_adaptation=False, use_cache=False),
        "D: Full TutorMind": AblationConfig(use_tarj=True, use_ecv=True, use_cdl=True, use_domain_adaptation=True, use_cache=False)
    }
    
    all_results = []
    
    for config_name, config in configs.items():
        print(f"\n--- Testing Configuration: {config_name} ---")
        
        for query in test_queries:
            # QUOTA GUARD
            if all_results:
                print("   ⏳ Respecting API quota (12s cooldown)...")
                await asyncio.sleep(12)

            print(f"  Query: {query}")
            start_time = time.time()
            
            response = await pipeline.run_pipeline(query, student_id="eval_user", config=config)
            
            latency = time.time() - start_time
            score = evaluate_response(query, response["explanation"])
            
            # Calculate Coverage %
            cov_rate = 0.0
            if config.use_ecv:
                # We need to perform the audit manually here because pipeline runs it in background
                report, _ = pipeline.quality_agent.perform_final_audit(query, response["explanation"], response["key_ideas"])
                total = len(report.covered_ideas) + len(report.missing_ideas)
                cov_rate = len(report.covered_ideas) / max(1, total) if total > 0 else 1.0
            else:
                # Baseline doesn't use key ideas, so coverage is technically N/A (set to 0)
                cov_rate = 0.0

            all_results.append({
                "Config": config_name,
                "Query": query,
                "Judge Score": score,
                "Coverage %": round(cov_rate * 100, 1),
                "Latency (s)": round(latency, 2)
            })

    # Summary Table
    df = pd.DataFrame(all_results)
    summary = df.groupby("Config").agg({
        "Judge Score": "mean",
        "Coverage %": "mean",
        "Latency (s)": "mean"
    }).reset_index()

    print("\n" + "="*60)
    print("📊 FINAL ABLATION SUMMARY (Scientific Mode)")
    print("="*60)
    print(summary.to_string(index=False))
    
    os.makedirs("evaluation/results", exist_ok=True)
    summary.to_csv("evaluation/results/final_ablation_summary.csv", index=False)
    print(f"\n✅ Results saved to evaluation/results/final_ablation_summary.csv")

if __name__ == "__main__":
    asyncio.run(run_ablation_study())
