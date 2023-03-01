# RenPaC Development Standards

## Python

- class names are ProperCase
- all other variables and functions are lower_case_with_underscores
- always use @staticmethod or @classmethod on relevant functions
- only import local classes with `from . import X`
    - NEVER import local classes with `import X`
    - NEVER import local globals or functions with `from . import my_func`
    - deviating from these guidelines will break the `*.py` => `*.gen.rpy` generator
- if a class is in pure python, create a `.py` file
- one class per file
- use classes for functions and variables accessible in other Python files or in Ren'Py
    - use static functions and class variables for singleton cases
    - only create global functions and variables for use in the same file
- after renaming a .py file, run `generate.bat` or `generate.sh` to clean up
- when calling Ren'Py methods, use `#type: ignore` at the end of the line to remove the "can't find `renpy`" warning
    - DO NOT use `#type: ignore` on any other line; instead, use the relevant `import` or `from . import`
    - this ensures the generator calculates the correct priorities for local dependencies
- avoid handling animations, rendering, or dialogue in Python when possible; instead, call a Ren'Py label

## Ren'Py

- use Ren'Py labels only if needed from screen actions etc.
    - minimize the length of scripts in labels unless they are dialogue or animation
    - pass control to Python as early as possible and as few times as possible per label 
- ALWAYS put `return` to terminate a label to prevent pass through