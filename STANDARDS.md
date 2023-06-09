# RenPaC Development Standards

- when no logical order is required, order alphabetically

## Logging

- INFO: informing a technical user about what the software is doing
- DEBUG: additional information to check things are working
- begin messages lowercase unless specifying an operation in all caps i.e. DELETE

## Config Design

- user-facing scripts should be as simple as possible
- break into small, understandable sections (game, debug, etc.)
- discourage the use of paired elements (parentheses, braces, brackets, quotes)
- keys should be:
    - a single word to avoid awkward double words or underscores (level, not loglevel or log_level)
    - context-aware in their section (debug.level suggests relationship to the log)
    - easy to distinguish and easy to spell (path instead of directory)

## Issues

- for a bug, name the issue after what's going wrong
    - avoid starting with "Fix"
    - example:
        - bad: "The button should be purple"
        - also bad: "Fix the button being red instead of purple"
        - okay: "The button is red"
        - good: "The button is red, but should be purple"
- for a feature, name the issue after the action that the code will be performing to avoid needless words
    - avoid starting with "Implement" as "Add" or "Change" is more accurate
    - example:
        - bad: "Implement back button"
        - okay: "User clicks back button to go back"
        - good: "Add back button which allows user to go back"
- avoid modifying issue descriptions or comments after creation
    - for additional information, write a new comment (to preserve history)
    - when removing information, strike it through add a new explanatory comment
    - technical corrections like spelling, grammar, and formatting are okay
- if an issue is closed manually:
    - always close in the project manager with an explanatory comment to sync repos and projects
    - use "Close as not planned" if the issue was not actually resolved
- always set milestone before marking as done
    - every "done" issue must be in a milestone, even if it's a wontfix
    - if the issue is in a future milestone, move it back to the current before closing
    - future milestones should only have open issues

## Python

- files:
    - files with lowercase name should be a collection of functions under a single concept
        - i.e. `files.py` defines file operations like `copy_tree()`
        - import these files as a module namespace, i.e. `from renpac.base import files`
            - in this case, you would call `files.copy_tree()`
        - do not import like `import renpac.base.files`
            - this would require `renpac.base.copy_tree()` for each call
        - do not import like `from renpac.base.files import copy_tree`
            - this makes imports difficult to maintain and puts `copy_tree()`
              into the global namespace
        - do not import like `from renpac.base.files import *`
            - this is extra terrible because it puts *everything* from the
              module into the global namespace and it is difficult to see what
              is available
    - files wil uppercase name should contain *only* a single class matching that name
        - i.e. `StaticClass.py` defines `StaticClass`
        - import the class, not the module
            - never `from renpac.base.StaticClass import StaticClass` 
            - or `from renpac.base.StaticClass import *` 
        - do not import like `import renpac.base.StaticClass`
            - this requires `StaticClass.StaticClass` for every reference
    - when multiple classes form a cohesive collection, it is acceptable to use
      a lowercase namespace module to group them: i.e. `python`
        - in this case, follow the rules for importing lowercase modules
            - i.e. `from renpac.base import python`
            - then `python.Value`, `python.Object`, etc.
- avoid lambdas when possible
    - they cannot be pickled (which Ren'py may need to do for saving game data)
    - the mypy type checker can be overly strict with them and require weird typing
    - syntax can get ugly quickly with all proper type hints in place
- always use type hints for arguments and return types for better error checking
- always use type hint with a new variable to avoid redefinition later
- imports
    - order from less specific to more specific
        - builtin python, renpac base, current project (i.e. renpac engine)
        - within each: import, from X import *, from X import Y
        - leave a blank line between each of these sections
    - within a single line of imports, list alphabetically with classes grouped first
        - from foo import Bar, Duck, Zoo, add_foo, set_size
- avoid lines longer than the preset minimum (use gql to check)
    - if a single code line runs multiple lines, indent subsequent lines one deeper that the first
        - remember in some casese parentheses are required to notify Python these are a single line
    - always split *after* a paired token (paren, bracket, brace) or comma
    - always split *before* a calculation operator (+ - * / %)
    - never put a function return type on its own line (treat it as "attached" to the last argument)
    - never split a compound type like `Callable[[int, str], bool]`
- strings
    - use backslashes instead of parentheses for multiline string literals
        - this helps avoid missing commas in a list (there will always be a comma or a backslash)
        - do this even if the strings are wrapped in a required container (parentheses, brackets, etc.)
        - bad if `foo` is a `str`:
            ```py
            foo = ("this is a string that "
                "goes on to the next line")
            ```
            - we could misinterpret it for the `List[str]`:
                ```py
                foo = ("this is a string that ",
                    "goes on to the next line")
                ```
        - instead:
            foo = "this is a string that " \
                "goes on to the next line"
    - use `join()` instead of `+`
        - bad: 
            ```py
            foo = "hello " + "world"
            ```
        - good: 
            ```py
            foo = ' '.join("hello", "world")
            ```
- files should be ordered: global variables, class definitions, functions, loose script
    - loose script should be avoided if possible and put in the main() test function
- every file must have tests in a block at the end starting:
    ```py
    if __name__ == "__main__":
    ```
    - if no tests are currently implemented, print "no tests available"
    - if tests are known to be incomplete, print "(tests incomplete)" after all testing concludes
- class names are ProperCase
- all other variables and functions are lower_case_with_underscores
- always use @staticmethod or @classmethod on relevant functions
- specific to engine
    - all imports must be `from base import X` for elements from `base` and `from . import X` for elements from `engine`
    - deviating from this will break the generator
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
- use "double quotes" for strings except:
    - single character strings like 'm'
    - dictionary keys like `my_dict['my key']`
- always use type hinting for variables and return types
    - if the type hinting doesn't work, try putting it in single quotes
- avoid nested functions
    - they might be useful in extreme edge cases but they're weird in python

## Ren'Py

- use Ren'Py labels only if needed from screen actions etc.
    - minimize the length of scripts in labels unless they are dialogue or animation
    - pass control to Python as early as possible and as few times as possible per label 
- ALWAYS put `return` to terminate a label to prevent pass through

## Git

- err on the side of too many commits instead of too few
- ideally, make a single commit to close an issue on GitHub
    - use the format `keyword #123 - description of commit`
- for intermediary commits, reference the relevant issue
    - example: `Ref #396 - prepare base class for implementation`
- use the correct keyword to close issues
    - `Fix` for bug
    - `Close` for feature
    - `Resolve` for documentation or question

## Doxygen

- use ## for variable comments and """! """ for function comments
- in function comments:
    - put a blank line between the three major sections: description, paramaters, and return
    - only put a blank line between parameter descriptions if it runs more than one line
    - for multi-line parameter descriptions, indent all lines after the first
    - generally, follow the standard set out in `Rect.py`
