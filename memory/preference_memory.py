import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional


DB_PATH = Path("data/student.db")


def _connect():
    """
    Creates a database connection.
    Also makes sure the data folder exists.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_preference_table():
    """
    Creates the preference_memory table if it does not already exist.

    This prevents errors when save_preference() is called before the table
    has been created by another database initialization file.
    """
    conn = _connect()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS preference_memory (
            student_id TEXT NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            evidence_count INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id, preference_key)
        )
        """
    )

    conn.commit()
    conn.close()


def save_preference(
    student_id: str,
    key: str,
    value: str,
    confidence: float = 1.0
) -> None:
    """
    Saves or updates a student preference.

    If the same student already has the same preference key,
    the value is updated and evidence_count increases by 1.
    """

    if not student_id:
        student_id = "default_student"

    if not key or not value:
        return

    create_preference_table()

    conn = _connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO preference_memory (
            student_id,
            preference_key,
            preference_value,
            confidence,
            evidence_count,
            updated_at
        )
        VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, preference_key)
        DO UPDATE SET
            preference_value = excluded.preference_value,
            confidence = excluded.confidence,
            evidence_count = preference_memory.evidence_count + 1,
            updated_at = CURRENT_TIMESTAMP
        """,
        (student_id, key, value, confidence),
    )

    conn.commit()
    conn.close()


def get_preferences(student_id: str) -> List[Tuple[str, str, float]]:
    """
    Returns preferences for a student as tuples:
    (preference_key, preference_value, confidence)
    """

    if not student_id:
        student_id = "default_student"

    create_preference_table()

    conn = _connect()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT preference_key, preference_value, confidence
        FROM preference_memory
        WHERE student_id = ?
        ORDER BY updated_at DESC
        """,
        (student_id,),
    )

    preferences = cur.fetchall()
    conn.close()

    return preferences


def get_preferences_dict(student_id: str) -> Dict[str, str]:
    """
    Returns preferences as a dictionary.

    Example:
    {
        "answer_length": "short",
        "explanation_style": "simple"
    }
    """

    rows = get_preferences(student_id)

    return {
        key: value
        for key, value, confidence in rows
    }


def detect_preferences_from_message(message: str) -> List[Tuple[str, str, float]]:
    """
    Simple rule-based preference detector.

    It extracts learning preferences from the student's message.
    """

    if not message:
        return []

    text = message.lower()
    detected = []

    if "simple" in text or "explain simply" in text or "easy" in text:
        detected.append(("explanation_style", "simple", 0.9))

    if "brief" in text or "short" in text or "summarize" in text:
        detected.append(("answer_length", "short", 0.9))

    if "detailed" in text or "deep" in text or "in depth" in text:
        detected.append(("answer_length", "detailed", 0.9))

    if "example" in text or "examples" in text:
        detected.append(("learning_style", "examples", 0.85))

    if "mcq" in text or "multiple choice" in text or "quiz" in text:
        detected.append(("practice_style", "mcq", 0.85))

    if "equation" in text or "formula" in text:
        detected.append(("learning_style", "equations", 0.8))

    if "step by step" in text or "steps" in text:
        detected.append(("explanation_style", "step_by_step", 0.9))

    return detected


def save_detected_preferences(student_id: str, message: str) -> List[Tuple[str, str, float]]:
    """
    Detects preferences from a user message and saves them.

    Returns the detected preferences so the pipeline/UI can display them if needed.
    """

    detected_preferences = detect_preferences_from_message(message)

    for key, value, confidence in detected_preferences:
        save_preference(
            student_id=student_id,
            key=key,
            value=value,
            confidence=confidence,
        )

    return detected_preferences


def clear_preferences(student_id: str) -> None:
    """
    Deletes all preferences for a student.
    Useful for testing.
    """

    if not student_id:
        student_id = "default_student"

    create_preference_table()

    conn = _connect()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM preference_memory
        WHERE student_id = ?
        """,
        (student_id,),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Small manual test
    test_student = "student_001"
    test_message = "Explain LSTM simply, step by step, with examples and MCQs."

    saved = save_detected_preferences(test_student, test_message)

    print("Saved preferences:")
    print(saved)

    print("\nCurrent preferences:")
    print(get_preferences(test_student))

    print("\nPreferences as dictionary:")
    print(get_preferences_dict(test_student))