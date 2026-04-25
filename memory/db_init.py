import sqlite3
import os
from pathlib import Path

DB_PATH = "data/student.db"

def init_db():
    """
    Initializes the master student database with all required tables.
    """
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    print(f"🗄️ Initializing Master Student Database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Concept Debt Ledger (CDL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concept_debt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        prerequisite_concept TEXT NOT NULL,
        severity INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 5),
        evidence TEXT,
        status TEXT DEFAULT 'open' CHECK(status IN ('open','partial','repaired')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, topic, prerequisite_concept)
    )
    """)

    # 2. Weak Topic Tracker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weak_topics (
        student_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        difficulty REAL DEFAULT 5.0,
        interactions INTEGER DEFAULT 0,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (student_id, topic)
    )
    """)

    # 3. Preference Memory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preference_memory (
        student_id TEXT NOT NULL,
        preference_key TEXT NOT NULL,
        preference_value TEXT,
        confidence REAL DEFAULT 0.0,
        evidence_count INTEGER DEFAULT 0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (student_id, preference_key)
    )
    """)

    # 4. Session History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS session_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        query TEXT NOT NULL,
        summary TEXT,
        key_ideas_covered TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
