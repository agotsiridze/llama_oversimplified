def skip(message: str) -> str:
    if message == 0:
        return ""
    if message == 9:
        return None
    return message
