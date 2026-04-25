import json
from pathlib import Path
from typing import Dict, List

from schemas import DebtEntry


GRAPH_PATH = Path("data/prerequisite_graph.json")


def load_prerequisite_graph(path: str | Path = GRAPH_PATH) -> Dict[str, List[str]]:
    """
    Loads the manually written prerequisite graph.
    """

    path = Path(path)

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def detect_concept_debt(
    topic: str,
    missing_ideas: List[str],
    graph: Dict[str, List[str]] | None = None,
) -> List[DebtEntry]:
    """
    Detects concept debt by comparing missing ideas with known prerequisites.
    """

    if graph is None:
        graph = load_prerequisite_graph()

    prerequisites = graph.get(topic, [])

    debts = []

    for missing_idea in missing_ideas:
        missing_lower = missing_idea.lower()

        for prerequisite in prerequisites:
            prerequisite_lower = prerequisite.lower()

            if prerequisite_lower in missing_lower or missing_lower in prerequisite_lower:
                debts.append(
                    DebtEntry(
                        topic=topic,
                        missing_concept=prerequisite,
                        reason=(
                            f"The student seems weak in '{prerequisite}', "
                            f"which is a prerequisite for understanding '{topic}'."
                        ),
                        severity=4,
                    )
                )

    existing_concepts = {debt.missing_concept for debt in debts}

    for missing_idea in missing_ideas:
        matched = False

        for prerequisite in prerequisites:
            if prerequisite.lower() in missing_idea.lower():
                matched = True
                break

        if not matched and missing_idea not in existing_concepts:
            debts.append(
                DebtEntry(
                    topic=topic,
                    missing_concept=missing_idea,
                    reason=(
                        f"The explanation or student answer missed this important idea: {missing_idea}."
                    ),
                    severity=3,
                )
            )

    return debts


def debt_entries_to_dicts(debts: List[DebtEntry]) -> List[dict]:
    """
    Converts DebtEntry objects into dictionaries.
    Useful for saving to SQLite or showing in Streamlit.
    """

    return [
        {
            "topic": debt.topic,
            "missing_concept": debt.missing_concept,
            "reason": debt.reason,
            "severity": debt.severity,
        }
        for debt in debts
    ]