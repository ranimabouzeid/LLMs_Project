import sqlite3
import pandas as pd

def check_database():
    db_path = "data/student.db"
    conn = sqlite3.connect(db_path)
    
    print("\n" + "="*50)
    print("📜 SESSION HISTORY (Last 3 entries)")
    print("="*50)
    history = pd.read_sql_query("SELECT id, timestamp, query, summary FROM session_history ORDER BY id DESC LIMIT 3", conn)
    print(history.to_string(index=False))

    print("\n" + "="*50)
    print("📈 WEAK TOPICS")
    print("="*50)
    weak = pd.read_sql_query("SELECT topic, difficulty, interactions FROM weak_topics", conn)
    print(weak.to_string(index=False))

    print("\n" + "="*50)
    print("💸 CONCEPT DEBT LEDGER (Active Debts)")
    print("="*50)
    debt = pd.read_sql_query("SELECT topic, prerequisite_concept, severity, status FROM concept_debt", conn)
    if debt.empty:
        print("No debts recorded yet (this is good, it means you covered everything!)")
    else:
        print(debt.to_string(index=False))

    conn.close()

if __name__ == "__main__":
    check_database()
