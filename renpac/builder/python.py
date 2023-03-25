import string
import re

from typing import Optional

def combo(n: str) -> str:
    return name("combo", n)

def exit(n: str) -> str:
    return name("exit", n)
    
def item(n: str) -> str:
    return name("item", n)

def name(type: Optional[str], n: str) -> str:
    n = n.strip()
    chars = re.escape(string.punctuation + string.whitespace)
    n = re.sub('['+chars+']', '_', n)
    while "__" in n:
        n = n.replace("__", "_")
    if type is None:
        return n
    return f"{type}_{n}"

def room(n: str) -> str:
    return name("room", n)

if __name__ == "__main__":
    while True:
        n = input("Name (empty to quit): ")
        if len(n) == 0:
            break
        print("No type:", name(None, n))
        print("Type 'foo':", name("foo", n))