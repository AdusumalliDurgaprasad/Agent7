import sqlite3
import uuid
from pathlib import Path
from datetime import datetime


# ==================================================
# DATABASE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "jobs" / "agent7_jobs.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==================================================
# INITIALIZE CONVERSATION MEMORY
# ==================================================

def initialize_conversation_memory():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
            REFERENCES conversations(conversation_id)
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# START CONVERSATION
# ==================================================

def start_conversation(title="New Conversation"):

    conversation_id = str(
        uuid.uuid4()
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations
        (
            conversation_id,
            title
        )
        VALUES (?, ?)
    """, (
        conversation_id,
        title
    ))

    conn.commit()
    conn.close()

    return conversation_id


# ==================================================
# SAVE MESSAGE
# ==================================================

def save_message(
    conversation_id,
    role,
    message
):

    if role not in [
        "user",
        "assistant",
        "system"
    ]:

        raise ValueError(
            "Role must be user, assistant, or system."
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversation_messages
        (
            conversation_id,
            role,
            message
        )
        VALUES (?, ?, ?)
    """, (
        conversation_id,
        role,
        message
    ))

    cursor.execute("""
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE conversation_id = ?
    """, (
        conversation_id,
    ))

    conn.commit()
    conn.close()


# ==================================================
# GET CONVERSATION
# ==================================================

def get_conversation(conversation_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            role,
            message,
            created_at
        FROM conversation_messages
        WHERE conversation_id = ?
        ORDER BY id ASC
    """, (
        conversation_id,
    ))

    messages = cursor.fetchall()

    conn.close()

    return messages


# ==================================================
# GET RECENT MESSAGES
# ==================================================

def get_recent_messages(
    conversation_id,
    limit=10
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            role,
            message,
            created_at
        FROM conversation_messages
        WHERE conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        conversation_id,
        limit
    ))

    messages = cursor.fetchall()

    conn.close()

    # Database returns newest first.
    # Reverse them so AI receives
    # the conversation chronologically.

    messages.reverse()

    return messages


# ==================================================
# GET ALL CONVERSATIONS
# ==================================================

def get_all_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            conversation_id,
            title,
            created_at,
            updated_at,
            active
        FROM conversations
        ORDER BY updated_at DESC
    """)

    conversations = cursor.fetchall()

    conn.close()

    return conversations


# ==================================================
# END CONVERSATION
# ==================================================

def end_conversation(conversation_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE conversations
        SET active = 0
        WHERE conversation_id = ?
    """, (
        conversation_id,
    ))

    conn.commit()

    changed = cursor.rowcount

    conn.close()

    return changed > 0


# ==================================================
# GET ACTIVE CONVERSATION
# ==================================================

def get_active_conversation():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            conversation_id,
            title,
            created_at,
            updated_at
        FROM conversations
        WHERE active = 1
        ORDER BY updated_at DESC
        LIMIT 1
    """)

    conversation = cursor.fetchone()

    conn.close()

    return conversation


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print("\n===================================")
    print("    AGENT7 CONVERSATION MEMORY")
    print("===================================")

    # Initialize tables

    initialize_conversation_memory()

    # Start conversation

    conversation_id = start_conversation(
        "Agent7 Test Conversation"
    )

    print(
        "\nConversation ID:"
    )

    print(
        conversation_id
    )

    # Save user message

    save_message(
        conversation_id,
        "user",
        "Find me AI internships."
    )

    # Save Agent7 response

    save_message(
        conversation_id,
        "assistant",
        "I found several AI internship opportunities."
    )

    # Save another user message

    save_message(
        conversation_id,
        "user",
        "Only show remote opportunities."
    )

    # Save another response

    save_message(
        conversation_id,
        "assistant",
        "Sure. I will focus on remote AI internships."
    )

    # --------------------------------------------------
    # SHOW COMPLETE CONVERSATION
    # --------------------------------------------------

    print(
        "\n-----------------------------------"
    )

    print(
        "COMPLETE CONVERSATION"
    )

    print(
        "-----------------------------------"
    )

    messages = get_conversation(
        conversation_id
    )

    for role, message, timestamp in messages:

        print(
            f"\n[{role}]"
        )

        print(
            message
        )

    # --------------------------------------------------
    # SHOW RECENT MEMORY
    # --------------------------------------------------

    print(
        "\n-----------------------------------"
    )

    print(
        "RECENT CONVERSATION MEMORY"
    )

    print(
        "-----------------------------------"
    )

    recent = get_recent_messages(
        conversation_id,
        limit=3
    )

    for role, message, timestamp in recent:

        print(
            f"[{role}] {message}"
        )

    # --------------------------------------------------
    # SHOW ACTIVE CONVERSATION
    # --------------------------------------------------

    print(
        "\n-----------------------------------"
    )

    print(
        "ACTIVE CONVERSATION"
    )

    print(
        "-----------------------------------"
    )

    print(
        get_active_conversation()
    )

    print(
        "\nConversation memory test complete."
    )