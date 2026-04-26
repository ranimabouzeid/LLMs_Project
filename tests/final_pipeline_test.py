import asyncio
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from pipeline.teaching_pipeline import pipeline

def run_final_test():
    print("\n" + "="*50)
    print("🎓 DEEPSTUDY COACH - FINAL INTEGRATION TEST")
    print("="*50)

    query = "What is the difference between an LSTM and a GRU?"
    student_id = "test_student_001"

    try:
        # FIXED: Using asyncio.run to call the new async pipeline
        result = asyncio.run(pipeline.run_pipeline(query, student_id=student_id))

        print("\n--- EXPLANATION ---")
        print(result["explanation"])

        print("\n--- SOURCES ---")
        for i, source in enumerate(result["sources"], 1):
            name = getattr(source, 'source_file', 'Unknown')
            score = getattr(source, 'pedagogical_score', 0)
            print(f"[{i}] {name} (Score: {score:.1f}/10)")

        print("\n--- COVERAGE ---")
        if result["coverage"]:
            report = result["coverage"]
            print(f"Status: {'✅ Complete' if report.is_complete else '⚠️ Missing Ideas'}")
            print(f"Covered: {', '.join(report.covered_ideas)}")
            if report.missing_ideas:
                print(f"Supplemented: {', '.join(report.missing_ideas)}")

        print("\n--- SELF-CHECK QUESTIONS ---")
        for i, q in enumerate(result["questions"], 1):
            if isinstance(q, dict):
                print(f"Q{i}: {q.get('question')}")
            else:
                print(f"Q{i}: {q}")

        print("\n" + "="*50)
        print("✅ INTEGRATION TEST PASSED")
        print("="*50)

    except Exception as e:
        print("\n" + "!"*50)
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        print("!"*50)

if __name__ == "__main__":
    run_final_test()
