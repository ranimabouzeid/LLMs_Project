import sqlite3

DB_PATH = "data/student.db"


def update_topic(student_id, topic, struggled=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT difficulty, interactions
        FROM weak_topics
        WHERE student_id = ? AND topic = ?
    """, (student_id, topic))

    row = cur.fetchone()

    if row is None:
        difficulty = 6.0 if struggled else 4.5
        interactions = 1

        cur.execute("""
            INSERT INTO weak_topics (student_id, topic, difficulty, interactions)
            VALUES (?, ?, ?, ?)
        """, (student_id, topic, difficulty, interactions))
    else:
        difficulty, interactions = row
        interactions += 1

        if struggled:
            difficulty = min(10.0, difficulty + 1.0)
        else:
            difficulty = max(0.0, difficulty - 0.5)

        cur.execute("""
            UPDATE weak_topics
            SET difficulty = ?, interactions = ?, last_seen = CURRENT_TIMESTAMP
            WHERE student_id = ? AND topic = ?
        """, (difficulty, interactions, student_id, topic))

    conn.commit()
    conn.close()


def get_weak_topics(student_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT topic, difficulty, interactions, last_seen
        FROM weak_topics
        WHERE student_id = ?
        ORDER BY difficulty DESC
        LIMIT ?
    """, (student_id, limit))

    topics = cur.fetchall()
    conn.close()

    return topics