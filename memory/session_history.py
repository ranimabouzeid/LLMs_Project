import sqlite3

DB_PATH = "data/student.db"


def save_session(student_id, topic, summary):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO session_history (student_id, topic, summary)
        VALUES (?, ?, ?)
    """, (student_id, topic, summary))

    conn.commit()
    conn.close()


def get_recent_sessions(student_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT query, summary, timestamp
        FROM session_history
        WHERE student_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (student_id, limit))

    sessions = cur.fetchall()
    conn.close()

    return sessions