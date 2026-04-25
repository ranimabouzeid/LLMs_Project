from typing import List

from schemas import CoverageReport, KeyIdea


def verify_coverage(
    key_ideas: List[KeyIdea],
    explanation: str,
    threshold: float = 0.75,
) -> CoverageReport:
    """
    ECV: Explanation Coverage Verifier.

    It checks whether the generated explanation covers the required key ideas.
    This version is rule-based and does not require Gemini.
    """

    if not key_ideas:
        return CoverageReport(
            is_complete=True,
            score=1.0,
            covered_ideas=[],
            missing_ideas=[],
            feedback="No key ideas were provided, so coverage is considered complete.",
        )

    explanation_lower = explanation.lower()

    covered = []
    missing = []

    for idea in key_ideas:
        idea_text = idea.text.strip()
        idea_words = [
            word.strip(".,:;!?()[]{}").lower()
            for word in idea_text.split()
            if len(word.strip(".,:;!?()[]{}")) > 3
        ]

        if not idea_words:
            missing.append(idea_text)
            continue

        matched_words = 0

        for word in idea_words:
            if word in explanation_lower:
                matched_words += 1

        idea_score = matched_words / len(idea_words)

        if idea_score >= 0.5:
            covered.append(idea_text)
        else:
            missing.append(idea_text)

    score = len(covered) / len(key_ideas)
    is_complete = score >= threshold

    if is_complete:
        feedback = "The explanation covers the main required ideas."
    else:
        feedback = (
            "The explanation is incomplete. It should be improved by adding the missing ideas."
        )

    return CoverageReport(
        is_complete=is_complete,
        score=score,
        covered_ideas=covered,
        missing_ideas=missing,
        feedback=feedback,
    )


def build_coverage_feedback(report: CoverageReport) -> str:
    """
    Converts a CoverageReport into readable feedback.
    """

    lines = []

    lines.append(f"Coverage score: {report.score:.2f}")
    lines.append(f"Complete: {report.is_complete}")
    lines.append(report.feedback)

    if report.covered_ideas:
        lines.append("\nCovered ideas:")
        for idea in report.covered_ideas:
            lines.append(f"- {idea}")

    if report.missing_ideas:
        lines.append("\nMissing ideas:")
        for idea in report.missing_ideas:
            lines.append(f"- {idea}")

    return "\n".join(lines)