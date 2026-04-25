from pipeline.teaching_pipeline import pipeline

def run_final_test():
    student_query = "Can you explain the difference between RNNs and Transformers?"
    
    result = pipeline.run_pipeline(student_query)
    
    print("\n" + "="*50)
    print("🎓 DEEPSTUDY COACH RESPONSE")
    print("="*50)
    print(result["explanation"])
    print("\n" + "="*50)
    print(f"📚 Key Ideas Covered: {len(result['key_ideas'])}")
    print(f"📑 Sources Used: {len(result['sources'])}")
    print("="*50)

if __name__ == "__main__":
    run_final_test()
