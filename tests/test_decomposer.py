from agents.decomposer import Decomposer

def test_decomposer():
    decomposer = Decomposer()
    topic = "Transformers and Attention Mechanisms"
    
    print(f"⏳ Decomposing topic: '{topic}'...")
    key_ideas = decomposer.decompose(topic)
    
    print("\n✅ Successfully extracted Key Ideas:")
    for i, idea in enumerate(key_ideas, 1):
        print(f"{i}. {idea.name}: {idea.description}")

if __name__ == "__main__":
    test_decomposer()
