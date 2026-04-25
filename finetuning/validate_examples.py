"""
Validator for TutorMind domain Q&A examples.

Checks that finetuning/qa_examples.json is valid, non-empty,
and follows the required question-answer structure.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

QA_PATH = Path("finetuning/qa_examples.json")
MIN_EXAMPLES = 10


def _load_examples(path: Path) -> List[Dict[str, Any]]:
    """Load Q&A examples from a JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("qa_examples.json must contain a list of examples.")

    return data


def _validate_example(example: Dict[str, Any], index: int) -> None:
    """Validate one Q&A example."""
    if not isinstance(example, dict):
        raise ValueError(f"Example {index} must be a JSON object.")

    question = example.get("question")
    answer = example.get("answer")

    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"Example {index} is missing a valid question.")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError(f"Example {index} is missing a valid answer.")

    if len(answer.split()) < 25:
        raise ValueError(
            f"Example {index} answer is too short. "
            "Use tutor-style explanations, not one-line answers."
        )


def validate_examples() -> None:
    """Validate all Q&A examples."""
    examples = _load_examples(QA_PATH)

    if len(examples) < MIN_EXAMPLES:
        raise ValueError(
            f"Expected at least {MIN_EXAMPLES} examples, found {len(examples)}."
        )

    for index, example in enumerate(examples, start=1):
        _validate_example(example, index)

    print(f"Validated {len(examples)} Q&A examples successfully.")


if __name__ == "__main__":
    validate_examples()