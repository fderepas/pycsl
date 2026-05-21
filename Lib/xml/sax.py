"""PyCSL mock for Python's xml.sax module — Package containing SAX2 base classes and convenience functions."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def make_parser(parser_list: int) -> int:
    """Mock: Create and return a SAX :class:`~xml.sax.xmlreader.XMLReader` object.  The first parser found will be used.  If *parser_..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse(filename_or_stream: int, handler: int, error_handler: int) -> int:
    """Mock: Create a SAX parser and use it to parse a document.  The document, passed in as *filename_or_stream*, can be a filename ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parseString(string: int, handler: int, error_handler: int) -> int:
    """Mock: Similar to :func:`parse`, but parses from a buffer *string* received as a parameter.  *string* must be a :class:`str` in..."""
    return 0
