"""PyCSL mock for Python's csv module — Write and read tabular data to and from delimited files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def reader(csvfile: int, dialect: int) -> int:
    """Mock: Return a :ref:`reader object <reader-objects>` that will process lines from the given *csvfile*.  A csvfile must be an i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def writer(csvfile: int, dialect: int) -> int:
    """Mock: Return a writer object responsible for converting the user's data into delimited strings on the given file-like object. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_dialect(name: int, dialect: int) -> int:
    """Mock: Associate *dialect* with *name*.  *name* must be a string. The dialect can be specified either by passing a sub-class of..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister_dialect(name: int) -> int:
    """Mock: Delete the dialect associated with *name* from the dialect registry.  An :exc:`Error` is raised if *name* is not a regis..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_dialect(name: int) -> int:
    """Mock: Return the dialect associated with *name*.  An :exc:`Error` is raised if *name* is not a registered dialect name.  This ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def list_dialects() -> int:
    """Mock: Return the names of all registered dialects."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def field_size_limit() -> int:
    """Mock: Returns the current maximum field size allowed by the parser. If *new_limit* is given, this becomes the new limit."""
    return 0
