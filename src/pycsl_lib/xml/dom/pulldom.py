"""PyCSL mock for Python's xml.dom.pulldom module — Support for building partial DOM trees from SAX events."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def parse(stream_or_string: int, parser: int, bufsize: int) -> int:
    """Mock: Return a :class:`DOMEventStream` from the given input. *stream_or_string* may be either a file name, or a file-like obje..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parseString(string: int, parser: int) -> int:
    """Mock: Return a :class:`DOMEventStream` that represents the (Unicode) *string*."""
    return 0
