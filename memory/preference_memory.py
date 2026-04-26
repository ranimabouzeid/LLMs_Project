import sqlite3

DB_PATH = "data/student.db"

def save_preference(student_id, key, value, confidence=1.0):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO preference_memory (student_id, preference_key, preference_value, confidence, evidence_count, updated_at)
            VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, preference_key)
            DO UPDATE SET
                preference_value = excluded.preference_value,
                confidence = excluded.confidence,
                evidence_count = evidence_count + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (student_id, key, value, confidence))
        conn.commit()

def get_preferences(student_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT preference_key, preference_value, confidence
            FROM preference_memory
            WHERE student_id = ?
        """, (student_id,))
        return cur.fetchall()
