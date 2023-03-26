from typing import Optional

def wrap(text: str, initial: str, terminal: Optional[str] = None) -> str:
    if terminal is None:
        terminal = initial
    return f"{initial}{text}{terminal}"