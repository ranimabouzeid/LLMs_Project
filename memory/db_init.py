import sqlite3
import os
from pathlib import Path

DB_PATH = "data/student.db"

def init_db():
    """
    Initializes and MIGRATES the master student database.
    """
    Path("data").mkdir(exist_ok=True)
    print(f"🗄️ Initializing/Migrating Master Student Database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Concept Debt Ledger (CDL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concept_debt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        prerequisite_concept TEXT NOT NULL,
        severity INTEGER NOT NULL,
        evidence TEXT,
        status TEXT DEFAULT 'open',
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

    # 5. Knowledge Cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_cache (
        query_hash TEXT PRIMARY KEY,
        key_ideas_json TEXT,
        approved_chunks_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready.")

def force_fix_constraints():
    """
    Recreates the concept_debt table to ensure the 0-5 constraint is active.
    """
    if not os.path.exists(DB_PATH):
        return
        
    print("🔧 Migrating concept_debt table to allow severity=0...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Backup old data
        cursor.execute("SELECT * FROM concept_debt")
        old_data = cursor.fetchall()
        
        # 2. Drop old table
        cursor.execute("DROP TABLE concept_debt")
        
        # 3. Create new table with 0-5 constraint
        cursor.execute("""
        CREATE TABLE concept_debt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            prerequisite_concept TEXT NOT NULL,
            severity INTEGER NOT NULL CHECK(severity BETWEEN 0 AND 5),
            evidence TEXT,
            status TEXT DEFAULT 'open' CHECK(status IN ('open','partial','repaired')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, topic, prerequisite_concept)
        )
        """)
        
        # 4. Restore data (mapping columns)
        for row in old_data:
            cursor.execute("""
                INSERT INTO concept_debt (id, student_id, topic, prerequisite_concept, severity, evidence, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
            
        conn.commit()
        print("✅ Migration successful!")
    except Exception as e:
        print(f"⚠️ Migration skipped or failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    force_fix_constraints()
