import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from agents.debt_detector import detect_concept_debt
from agents.concept_debt_ledger import ConceptDebtLedger


def main():
    student_id = "student_001"
    topic = "LSTM"

    missing_ideas = [
        "Forget gate removes unnecessary information",
        "Cell state carries long term information",
        "Vanishing gradient problem"
    ]

    debts = detect_concept_debt(
        topic=topic,
        missing_ideas=missing_ideas
    )

    ledger = ConceptDebtLedger()
    ledger.add_debts(student_id, debts)

    print("=== Open Concept Debts ===")
    open_debts = ledger.get_open_debts(student_id)

    for debt in open_debts:
        print(debt)

    print("\n=== Debt Summary ===")
    summary = ledger.get_summary(student_id)
    print(summary)


if __name__ == "__main__":
    main()