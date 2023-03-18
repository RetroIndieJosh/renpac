class StaticClass:
    """! Prevent instatiation of a class that inherits this.
    """
    def __init__(self) -> None:
        """! Prevent an instance of the class from being created
        """
        raise Exception("Cannot instantiate a static class")
