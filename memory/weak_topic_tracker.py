import sqlite3

DB_PATH = "data/student.db"

def update_topic_score(student_id, topic, impact):
    """
    Updates the difficulty score for a topic. 
    Logic: +1.0 for struggle, -0.5 for mastery. 
    Clamped between 0.0 and 10.0 for UI professionality.
    """
    with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
        cur = conn.cursor()
        # We clamp the initial insert and the update to ensure no negative difficulty
        cur.execute("""
            INSERT INTO weak_topics (student_id, topic, difficulty, interactions)
            VALUES (?, ?, MAX(0.0, MIN(10.0, 5.0 + ?)), 1)
            ON CONFLICT(student_id, topic) DO UPDATE SET
                difficulty = MAX(0.0, MIN(10.0, difficulty + ?)),
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
