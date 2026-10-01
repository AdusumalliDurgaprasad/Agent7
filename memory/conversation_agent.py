import ollama

from conversation_memory import (
    initialize_conversation_memory,
    start_conversation,
    save_message
)

from memory_context import format_memory_for_ai


OLLAMA_MODEL = "gemma3:4b"


def generate_response(conversation_id, user_message):

    # Save user's message first
    save_message(
        conversation_id,
        "user",
        user_message
    )

    # Get complete memory context
    memory_context = format_memory_for_ai(
        conversation_id
    )

    system_message = f"""
You are Agent7, a personal AI assistant.

You have access to the user's recent conversation
and long-term memory.

Use this information to understand what the user
means and maintain continuity.

IMPORTANT RULES:

- Use previous context when relevant.
- If the user refers to something discussed earlier,
  connect it naturally.
- Use long-term memories when they are relevant.
- Do not mention the internal memory system.
- Do not invent memories.
- Do not claim to remember something that isn't provided.
- Answer naturally and directly.
- Do not unnecessarily repeat the user's previous messages.

Here is Agent7's memory context:

{memory_context}
"""

    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    try:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages
        )

    except Exception as e:

        print("\nOllama error:")
        print(e)

        return ""

    assistant_message = response[
        "message"
    ][
        "content"
    ].strip()

    # Save Agent7's response
    save_message(
        conversation_id,
        "assistant",
        assistant_message
    )

    return assistant_message


def start_chat():

    print("\n===================================")
    print("          AGENT7 MEMORY CHAT")
    print("===================================")

    initialize_conversation_memory()

    conversation_id = start_conversation(
        "Agent7 Interactive Chat"
    )

    print("\nConversation started.")

    print("Agent7 now has:")
    print("- Conversation memory")
    print("- Long-term memory")
    print("- Memory context")

    print("\nType 'exit' to end the conversation.")

    while True:

        user_message = input(
            "\nYou: "
        ).strip()

        if not user_message:
            continue

        if user_message.lower() == "exit":

            print("\nConversation ended.")
            break

        response = generate_response(
            conversation_id,
            user_message
        )

        if response:

            print(
                f"\nAgent7: {response}"
            )


if __name__ == "__main__":

    start_chat()