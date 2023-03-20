from typing import Optional

def combo(n: str) -> str:
    return name("combo", n)

def exit(n: str) -> str:
    return name("exit", n)
    
def item(n: str) -> str:
    return name("item", n)

def name(type: Optional[str], n: str) -> str:
    if type is None:
        return f"{n.strip()}".replace('.', '_').replace(' ', '_')
    return f"{type}_{n.strip()}".replace(' ', '_')

def room(n: str) -> str:
    return name("room", n)