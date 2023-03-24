from typing import List, Tuple

def text_menu(prompt: str, options: List[Tuple[str, str]]):
    message = prompt + '\n'
    for i in range(1, len(options)+1):
        message += f"[{i}] {options[i-1][0]}: {options[i-1][1]}\n"
    message += f"Enter a number [1-{i}]: "
    # TODO handle non int input
    selection = int(input(message))
    return options[selection-1][0]

if __name__ == "__main__":
    options = [
        ("print", "print a message"),
        ("quit", "quit testing"),
    ]
    result: str = ""
    while result != "quit":
        result = text_menu("Testing text menu", options)
        print(f"(result is {result})")
        if result == "print":
            print("a message")
    print("no tests available")