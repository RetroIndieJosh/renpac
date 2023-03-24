verbose = False

def enable_verbose():
    global verbose
    verbose = True
    printv("Verbose mode enabled")

def printv(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

if __name__ == "__main__":
    print("[Testing printv, no verbose]")
    printv("+ This is a message that should not appear")
    print("+ This is a message that should appear")
    print("+ There should be two messages starting with +")

    print("[Testing printv, verbose]")
    enable_verbose()
    print("* Verbose mode is now enabled")
    printv("* This should appear")
    print("* There should be three messages starting with *")

    print("[Testing printv end]")
    printv("This message should run on", end=' ')
    printv("to this message")
    printv("and this should be on a new line")
    printv("This message should", end=" not ")
    printv("end with a word", end='?')
    printv()
    printv()
    printv("and this should have a blank line above it")

    print("[Testing printv multiple elements]")
    printv("One", "Two", "Three", "Four")
    printv("1", "2", end=' ')
    printv("3", "4")
