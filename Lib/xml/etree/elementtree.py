"""PyCSL mock for Python's xml.etree.elementtree module — Implementation of the ElementTree API."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0 or \result == 1
def canonicalize(xml_data: int, out: int, from_file: int) -> int:
    """Mock: `C14N 2.0 <https://www.w3.org/TR/xml-c14n2/>`_ transformation function. Canonicalization is a way to normalise XML outpu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Comment(text: int) -> int:
    """Mock: Comment element factory.  This factory function creates a special element that will be serialized as an XML comment by t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dump(elem: int) -> int:
    """Mock: Writes an element tree or element structure to sys.stdout.  This function should be used for debugging only. The exact o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromstring(text: int, parser: int) -> int:
    """Mock: Parses an XML section from a string constant.  Same as :func:`XML`.  *text* is a string containing XML data.  *parser* i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromstringlist(sequence: int, parser: int) -> int:
    """Mock: Parses an XML document from a sequence of string fragments.  *sequence* is a list or other sequence containing XML data ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def indent(tree: int, space: int, level: int) -> int:
    """Mock: Appends whitespace to the subtree to indent the tree visually. This can be used to generate pretty-printed XML output. *..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def iselement(element: int) -> int:
    """Mock: Check if an object appears to be a valid element object.  *element* is an element instance.  Return ``True`` if this is ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def iterparse(source: int, events: int, parser: int) -> int:
    """Mock: Parses an XML section into an element tree incrementally, and reports what's going on to the user.  *source* is a filena..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse(source: int, parser: int) -> int:
    """Mock: Parses an XML section into an element tree.  *source* is a filename or file object containing XML data.  *parser* is an ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ProcessingInstruction(target: int, text: int) -> int:
    """Mock: PI element factory.  This factory function creates a special element that will be serialized as an XML processing instru..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_namespace(prefix: int, uri: int) -> int:
    """Mock: Registers a namespace prefix.  The registry is global, and any existing mapping for either the given prefix or the names..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SubElement(parent: int, tag: int, attrib: int) -> int:
    """Mock: Subelement factory.  This function creates an element instance, and appends it to an existing element. The element name,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tostring(element: int, encoding: int, method: int, __xml_declaration: int, default_namespace: int, __short_empty_elements: int) -> int:
    """Mock: Generates a string representation of an XML element, including all subelements.  *element* is an :class:`Element` instan..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def tostringlist(element: int, encoding: int, method: int, __xml_declaration: int, default_namespace: int, __short_empty_elements: int) -> int:
    """Mock: Generates a string representation of an XML element, including all subelements.  *element* is an :class:`Element` instan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XML(text: int, parser: int) -> int:
    """Mock: Parses an XML section from a string constant.  This function can be used to embed 'XML literals' in Python code.  *text*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XMLID(text: int, parser: int) -> int:
    """Mock: Parses an XML section from a string constant, and also returns a dictionary which maps from element id:s to elements.  *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def default_loader(href: int, parse: int, encoding: int) -> int:
    """Mock: Default loader. This default loader reads an included resource from disk. *href* is a URL.  *parse* is for parse mode ei..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def include(elem: int, loader: int, base_url: int, max_depth: int) -> int:
    """Mock: This function expands XInclude directives in-place in tree pointed by *elem*. *elem* is either the root :class:`~xml.etr..."""
    return 0
