from pipeline.teaching_pipeline import pipeline

def run_final_test():
    student_query = "What is the difference between an LSTM and a GRU?"
    
    result = pipeline.run_pipeline(student_query)
    
    print("\n" + "="*50)
    print("🎓 DEEPSTUDY COACH RESPONSE")
    print("="*50)
    print(result["explanation"])
    
    print("\n" + "="*50)
    print("❓ ASSESSMENT QUESTIONS")
    print("="*50)
    for i, q in enumerate(result["questions"], 1):
        if isinstance(q, dict): # MCQ
            print(f"\nQ{i} (MCQ): {q['question']}")
            for opt, text in q['options'].items():
                print(f"   {opt}: {text}")
        else: # Short Answer
            print(f"\nQ{i} (Short): {q}")

    print("\n" + "="*50)
    print(f"📚 Key Ideas Covered: {len(result['key_ideas'])}")
    print(f"📑 Sources Used: {len(result['sources'])}")
    print("="*50)

if __name__ == "__main__":
    run_final_test()
