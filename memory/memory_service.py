from memory_manager import (
    initialize_memory,
    remember,
    recall,
    forget,
    get_all_memories
)


class MemoryService:

    def __init__(self):
        initialize_memory()

    def remember_user_preference(self, key, value):
        remember(
            key,
            value,
            "user_preference"
        )

    def remember_career_information(self, key, value):
        remember(
            key,
            value,
            "career"
        )

    def remember_agent_action(self, key, value):
        remember(
            key,
            value,
            "agent_action"
        )

    def recall_memory(self, key):
        return recall(key)

    def forget_memory(self, key):
        return forget(key)

    def get_memories(self):
        return get_all_memories()


if __name__ == "__main__":

    print("\n===================================")
    print("      AGENT7 MEMORY SERVICE")
    print("===================================")

    memory = MemoryService()

    print("\nSaving user information...")

    memory.remember_user_preference(
        "comment_style",
        "Short, natural and professional"
    )

    memory.remember_career_information(
        "primary_goal",
        "Become an AI Engineer"
    )

    memory.remember_agent_action(
        "last_test",
        "Memory service tested successfully"
    )

    print("\nRecalling information:")

    print(
        "Comment style:",
        memory.recall_memory("comment_style")
    )

    print(
        "Career goal:",
        memory.recall_memory("primary_goal")
    )

    print("\nAll memories:")

    for item in memory.get_memories():
        print(item)

    print("\nMemory service test complete.")