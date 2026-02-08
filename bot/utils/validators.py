def is_valid_message(message: str) -> bool:
    """
    Validates a user message.
    """
    if not message or message.isspace():
        return False
    return True
