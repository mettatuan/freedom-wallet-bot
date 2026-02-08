from collections import deque
from config.settings import settings

conversation_histories = {}

def get_conversation_history(user_id: int):
    """
    Gets the conversation history for a user.
    """
    if user_id not in conversation_histories:
        conversation_histories[user_id] = deque(maxlen=settings.CONTEXT_MEMORY_SIZE)
    return conversation_histories[user_id]

def add_to_conversation_history(user_id: int, role: str, content: str):
    """
    Adds a message to the conversation history for a user.
    """
    history = get_conversation_history(user_id)
    history.append({"role": role, "content": content})

def clear_conversation_history(user_id: int):
    """
    Clears the conversation history for a user.
    """
    if user_id in conversation_histories:
        conversation_histories[user_id].clear()
