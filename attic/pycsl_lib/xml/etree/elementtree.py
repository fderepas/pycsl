"""PyCSL mock for Python's xml.etree.ElementTree module.

Element and ElementTree modelled as classes with invariants.
"""
_ = 0  # anchor

# ── ElementObj class ────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._children >= 0
class ElementObj:
    def __init__(self):
        self._children = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def tag(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def text(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def tail(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def attrib(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._children == \old(self._children) + 1
    #@ assigns self._children
    def append(self, subelement: int) -> int:
        self._children += 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def find(self, path: int, namespaces: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def findall(self, path: int, namespaces: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def findtext(self, path: int, default: int, namespaces: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self, key: int, default: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def set_attr(self, key: int, value: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def iter(self, tagfilter: int) -> int:
        return 0

# ── ElementTreeObj class ────────────────────────────────────────────

#@ class invariant self._parsed >= 0
class ElementTreeObj:
    def __init__(self):
        self._parsed = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def getroot(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._parsed == 1
    #@ assigns self._parsed
    def xml_parse(self, source: int, parser: int) -> int:
        self._parsed = 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def write(self, file_or_filename: int, encoding: int, xml_declaration: int, method: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def find(self, path: int, namespaces: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def findall(self, path: int, namespaces: int) -> int:
        return 0

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def fromstring(text: int, parser: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def tostring(element: int, encoding: int, method: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def xml_parse(source: int, parser: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def SubElement(parent: int, tag: int, attrib: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def iselement(element: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def iterparse(source: int, events: int, parser: int) -> int:
    return 0

#@ \trusted
#@ ensures \result == 0
def indent(tree: int, space: int, level: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def ParseError() -> int:
    return 0
