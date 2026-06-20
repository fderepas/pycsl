"""PyCSL mock for Python's xml.dom.minidom module — Minimal Document Object Model (DOM) implementation."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def parse(filename_or_file: int, parser: int, bufsize: int) -> int:
    """Mock: Return a :class:`Document` from the given input. *filename_or_file* may be either a file name, or a file-like object. *p..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parseString(string: int, parser: int) -> int:
    """Mock: Return a :class:`Document` that represents the *string*. This method creates an :class:`io.StringIO` object for the stri..."""
    return 0
