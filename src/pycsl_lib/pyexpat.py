"""PyCSL mock for Python's pyexpat module — An interface to the Expat non-validating XML parser."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def ErrorString(errno: int) -> int:
    """Mock: Returns an explanatory string for a given error number *errno*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ParserCreate(encoding: int, namespace_separator: int) -> int:
    """Mock: Creates and returns a new :class:`xmlparser` object.   *encoding*, if specified, must be a string naming the encoding  u..."""
    return 0
