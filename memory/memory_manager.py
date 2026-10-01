import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "jobs" / "agent7_jobs.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_key TEXT UNIQUE NOT NULL,
            memory_value TEXT NOT NULL,
            memory_type TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def remember(key, value, memory_type="general"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO agent_memory
        (memory_key, memory_value, memory_type)
        VALUES (?, ?, ?)
        ON CONFLICT(memory_key)
        DO UPDATE SET
            memory_value = excluded.memory_value,
            memory_type = excluded.memory_type,
            updated_at = CURRENT_TIMESTAMP
    """, (key, value, memory_type))

    conn.commit()
    conn.close()


def recall(key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT memory_value
        FROM agent_memory
        WHERE memory_key = ?
    """, (key,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


def forget(key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM agent_memory
        WHERE memory_key = ?
    """, (key,))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted > 0


def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT memory_key, memory_value, memory_type,
               created_at, updated_at
        FROM agent_memory
        ORDER BY updated_at DESC
    """)

    memories = cursor.fetchall()
    conn.close()

    return memories


if __name__ == "__main__":

    print("\n===================================")
    print("       AGENT7 MEMORY SYSTEM")
    print("===================================")

    initialize_memory()

    print("\nSaving test memory...")

    remember(
        "preferred_role",
        "AI Engineer",
        "career"
    )

    remember(
        "preferred_location",
        "India",
        "career"
    )

    print("\nRecalling memory...")

    role = recall("preferred_role")
    location = recall("preferred_location")

    print("Preferred role:", role)
    print("Preferred location:", location)

    print("\nAll memories:")

    for memory in get_all_memories():
        print(memory)

    print("\nTesting forget...")

    forget("preferred_location")

    print("Location after forget:",
          recall("preferred_location"))

    print("\nMemory system test complete.")