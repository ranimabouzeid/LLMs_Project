import sqlite3

DB_PATH = "data/student.db"

def update_topic_score(student_id, topic, impact):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weak_topics (student_id, topic, difficulty, interactions)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(student_id, topic) DO UPDATE SET
                difficulty = MAX(0, MIN(10, difficulty + ?)),
                interactions = interactions + 1,
                last_seen = CURRENT_TIMESTAMP
        """, (student_id, topic, impact, impact))
        conn.commit()

def get_weak_topics(student_id):
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT topic, difficulty, interactions, last_seen
            FROM weak_topics
            WHERE student_id = ?
            ORDER BY difficulty DESC
        """, (student_id,))
        return cur.fetchall()
