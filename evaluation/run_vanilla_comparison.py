import asyncio
import time
import pandas as pd
import os
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(os.getcwd())

from tools.llm_client import llm_client
from evaluation.llm_judge import evaluate_response

async def run_vanilla_comparison():
    print("🍦 [Evaluation] Starting Vanilla LLM (No Context) Comparison...")
    
    test_queries = [
        "What is the difference between an LSTM and a GRU?",
        "Why do we need softmax in classification?",
        "Explain backpropagation."
    ]
    
    results = []
    
    for query in test_queries:
        print(f"  Querying Vanilla LLM: {query}")
        start_time = time.time()
        
        # Pure LLM call, no RAG context, no special system prompt
        response = llm_client.chat(
            system_prompt="You are a helpful assistant.",
            user_message=query
        )
        
        latency = time.time() - start_time
        score = evaluate_response(query, response)
        
        results.append({
            "Judge Score": score,
            "Latency (s)": latency
        })
        
        # Quota guard
        print("  ⏳ Waiting for API cooldown...")
        await asyncio.sleep(12)

    avg_score = sum(r["Judge Score"] for r in results) / len(results)
    avg_latency = sum(r["Latency (s)"] for r in results) / len(results)

    # Load existing CSV
    csv_path = "evaluation/results/final_ablation_summary.csv"
    df = pd.read_csv(csv_path)
    
    # Create new row
    new_row = pd.DataFrame([{
        "Config": "Vanilla Gemini (No Context)",
        "Judge Score": round(avg_score, 2),
        "Coverage %": 0.0,
        "Latency (s)": round(avg_latency, 2)
    }])
    
    # Append and save
    df = pd.concat([new_row, df], ignore_index=True)
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*60)
    print("📊 UPDATED ABLATION SUMMARY WITH VANILLA BASELINE")
    print("="*60)
    print(df.to_string(index=False))
    print(f"\n✅ Results appended to {csv_path}")

if __name__ == "__main__":
    asyncio.run(run_vanilla_comparison())
