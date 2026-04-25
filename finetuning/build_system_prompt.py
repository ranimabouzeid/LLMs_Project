"""
Builds the TutorMind domain-adapted system prompt.

This script loads curated Q&A examples from finetuning/qa_examples.json
and writes a reusable teaching prompt to pipeline/domain_prompt.txt.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

QA_EXAMPLES_PATH = Path("finetuning/qa_examples.json")
OUTPUT_PROMPT_PATH = Path("pipeline/domain_prompt.txt")
DOMAIN = "Machine Learning and Deep Learning"


def load_qa_examples(path: Path) -> List[Dict[str, Any]]:
    """Load curated Q&A examples from a JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Q&A examples file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        examples = json.load(file)

    if not isinstance(examples, list):
        raise ValueError("Q&A examples must be stored as a JSON list.")

    return examples


def format_qa_examples(examples: List[Dict[str, Any]]) -> str:
    """Format Q&A examples into prompt-ready text."""
    formatted_blocks = []

    for index, example in enumerate(examples, start=1):
        question = str(example.get("question", "")).strip()
        answer = str(example.get("answer", "")).strip()

        if not question or not answer:
            raise ValueError(f"Invalid Q&A example at index {index}.")

        block = (
            f"EXAMPLE {index}\n"
            f"Student: {question}\n"
            f"Tutor: {answer}\n"
        )

        formatted_blocks.append(block)

    return "\n".join(formatted_blocks)


def build_system_prompt(examples: List[Dict[str, Any]]) -> str:
    """Build the complete domain-adapted system prompt."""
    examples_text = format_qa_examples(examples)

    return f"""
You are TutorMind, a domain-specific educational LLM tutor for {DOMAIN}.

Your role is not only to answer questions, but to teach for understanding.
Students often memorize chatbot answers without understanding the underlying concept.
Your job is to prevent that by explaining concepts clearly, checking conceptual coverage,
and addressing common misconceptions.

Teaching rules:
1. Build intuition before formulas.
2. Explain why the concept matters, not only what it is.
3. Break complex topics into key sub-ideas.
4. Use simple examples when helpful.
5. Warn about one common misconception when relevant.
6. Do not copy source wording directly.
7. Keep the explanation grounded in retrieved course material when provided.
8. If prerequisite gaps are provided, briefly repair them before the main answer.

Preferred response structure:
- Intuition
- Key idea walkthrough
- Concrete example
- Common misconception
- Short summary

The following examples define the expected teaching style.

{examples_text}
""".strip()


def save_prompt(prompt: str, output_path: Path) -> None:
    """Save the generated prompt to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        file.write(prompt)


def main() -> None:
    """Build and save the domain system prompt."""
    examples = load_qa_examples(QA_EXAMPLES_PATH)
    prompt = build_system_prompt(examples)
    save_prompt(prompt, OUTPUT_PROMPT_PATH)

    print(f"Built domain prompt with {len(examples)} examples.")
    print(f"Saved to: {OUTPUT_PROMPT_PATH}")


if __name__ == "__main__":
    main()