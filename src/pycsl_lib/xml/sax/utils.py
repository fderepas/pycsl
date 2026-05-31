"""PyCSL mock for Python's xml.sax.utils module — Convenience functions and classes for use with SAX."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def escape(data: int, entities: int) -> int:
    """Mock: Escape ``'&'``, ``'<'``, and ``'>'`` in a string of data. You can escape other strings of data by passing a dictionary a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unescape(data: int, entities: int) -> int:
    """Mock: Unescape ``'&amp;'``, ``'&lt;'``, and ``'&gt;'`` in a string of data. You can unescape other strings of data by passing ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def quoteattr(data: int, entities: int) -> int:
    """Mock: Similar to :func:`escape`, but also prepares *data* to be used as an attribute value.  The return value is a quoted vers..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prepare_input_source(source: int, base: int) -> int:
    """Mock: This function takes an input source and an optional base URL and returns a fully resolved :class:`~xml.sax.xmlreader.Inp..."""
    return 0
