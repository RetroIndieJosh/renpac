verbose = False

def enable_verbose():
    global verbose
    verbose = True

def printv(msg, end='\n'):
    if verbose:
        print(msg, end)
