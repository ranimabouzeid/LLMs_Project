import sqlite3

DB_PATH = "data/student.db"

def append_session(student_id, query, summary, key_ideas):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO session_history (student_id, query, summary, key_ideas_covered)
            VALUES (?, ?, ?, ?)
        """, (student_id, query, summary, str(key_ideas)))
        conn.commit()

def get_recent_sessions(student_id, limit=5):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT query, summary, timestamp
            FROM session_history
            WHERE student_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (student_id, limit))
        return cur.fetchall()
