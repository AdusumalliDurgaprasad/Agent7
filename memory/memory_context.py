from .conversation_memory import get_recent_messages
from .memory_manager import get_all_memories


MAX_CONVERSATION_MESSAGES = 10
MAX_LONG_TERM_MEMORIES = 20


def get_conversation_context(conversation_id):
    """
    Get recent messages from the current conversation.
    """

    messages = get_recent_messages(
        conversation_id,
        limit=MAX_CONVERSATION_MESSAGES
    )

    context = []

    for role, message, timestamp in messages:
        context.append({
            "role": role,
            "content": message
        })

    return context


def get_long_term_context():
    """
    Get important long-term memories.
    """

    memories = get_all_memories()

    context = []

    for memory in memories[:MAX_LONG_TERM_MEMORIES]:

        memory_key = memory[0]
        memory_value = memory[1]
        memory_type = memory[2]

        context.append({
            "key": memory_key,
            "value": memory_value,
            "type": memory_type
        })

    return context


def build_memory_context(conversation_id):
    """
    Build the complete memory context for Agent7.
    """

    conversation_context = get_conversation_context(
        conversation_id
    )

    long_term_context = get_long_term_context()

    return {
        "conversation": conversation_context,
        "long_term_memory": long_term_context
    }


def format_memory_for_ai(conversation_id):
    """
    Convert memory into a clean text context
    that can be given to the AI model.
    """

    memory = build_memory_context(
        conversation_id
    )

    context_text = ""

    # -----------------------------
    # Recent Conversation
    # -----------------------------

    context_text += "RECENT CONVERSATION:\n"

    if memory["conversation"]:

        for message in memory["conversation"]:

            role = message["role"]
            content = message["content"]

            context_text += (
                f"{role.upper()}: {content}\n"
            )

    else:

        context_text += "No previous conversation.\n"


    # -----------------------------
    # Long-Term Memory
    # -----------------------------

    context_text += "\nLONG-TERM MEMORY:\n"

    if memory["long_term_memory"]:

        for item in memory["long_term_memory"]:

            key = item["key"]
            value = item["value"]
            memory_type = item["type"]

            context_text += (
                f"- {key}: {value} "
                f"(type: {memory_type})\n"
            )

    else:

        context_text += "No long-term memories.\n"


    return context_text


if __name__ == "__main__":

    print("\n===================================")
    print("       AGENT7 MEMORY CONTEXT")
    print("===================================")

    print("\nThis module provides:")
    print("- Recent conversation context")
    print("- Long-term memory")
    print("- AI-ready memory context")

    print("\nMemory context layer is ready.")