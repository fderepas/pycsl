"""PyCSL mock for Python's xml.etree.ElementTree module."""
_ = 0  # anchor

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

#@ \trusted
def canonicalize(xml_data: str) -> str:
    """Mock: C14N 2.0 canonicalization — returns canonical XML string."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def Comment(text: str) -> int:
    """Mock: comment element factory — opaque Element."""
    return 0

#@ \trusted
#@ ensures \result == 0
def dump(elem: int) -> int:
    """Mock: writes element to stdout — side-effect."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromstring(text: str, parser: int) -> int:
    """Mock: parses XML from string — opaque Element."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromstringlist(sequence: int, parser: int) -> int:
    """Mock: parses XML from string fragments — opaque Element."""
    return 0

#@ \trusted
#@ ensures \result == 0
def indent(tree: int, space: str, level: int) -> int:
    """Mock: indents tree visually — side-effect."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iselement(element: int) -> int:
    """Mock: checks if object is element — boolean as int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iterparse(source: str, events: int, parser: int) -> int:
    """Mock: incremental XML parse — opaque iterator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse(source: str, parser: int) -> int:
    """Mock: parses XML file — opaque ElementTree."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ProcessingInstruction(target: str, text: str) -> int:
    """Mock: PI element factory — opaque Element."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_namespace(prefix: str, uri: str) -> int:
    """Mock: registers namespace prefix — side-effect."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SubElement(parent: int, tag: str, attrib: int) -> int:
    """Mock: subelement factory — opaque Element."""
    return 0

#@ \trusted
def tostring(element: int, encoding: str, method: str) -> str:
    """Mock: serializes element to XML string."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def tostringlist(element: int, encoding: str, method: str) -> int:
    """Mock: serializes element to list of strings — opaque list."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XML(text: str, parser: int) -> int:
    """Mock: parses XML literal — opaque Element."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XMLID(text: str, parser: int) -> int:
    """Mock: parses XML and returns (Element, id-dict) — opaque tuple."""
    return 0

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

#@ \trusted
#@ ensures \result >= 0
def Element(tag: str, attrib: int) -> int:
    """Mock: Element constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ElementTree(element: int, file: int) -> int:
    """Mock: ElementTree constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def QName(text_or_uri: str, tag: str) -> int:
    """Mock: QName constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TreeBuilder(element_factory: int) -> int:
    """Mock: TreeBuilder constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def C14NWriterTarget(write: int) -> int:
    """Mock: C14NWriterTarget constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XMLParser(target: int, encoding: str) -> int:
    """Mock: XMLParser constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def XMLPullParser(events: int) -> int:
    """Mock: XMLPullParser constructor — opaque."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ParseError() -> int:
    """Mock: ParseError exception — opaque."""
    return 0
