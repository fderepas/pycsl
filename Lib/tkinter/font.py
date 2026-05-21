"""PyCSL mock for Python's tkinter.font module — Tkinter font-wrapping class."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def families(root: int, displayof: int) -> int:
    """Mock: Return the different font families."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def names(root: int) -> int:
    """Mock: Return the names of defined fonts."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nametofont(name: int, root: int) -> int:
    """Mock: Return a :class:`Font` representation of a tk named font. .. versionchanged:: 3.10 The *root* parameter was added."""
    return 0
