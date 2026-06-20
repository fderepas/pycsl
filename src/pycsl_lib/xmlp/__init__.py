# Pure model for xml.etree.ElementTree — XML parsing
# Models Element as tag + child-count tracker.

""" # pycsl"""


#@ class invariant self._children >= 0
class Element:
    """Abstract XML element with tag and children count."""

    #@ requires tag >= 0
    #@ ensures self._tag == tag
    #@ ensures self._children == 0
    #@ ensures self._text == 0
    def __init__(self, tag: int) -> None:
        self._tag: int = tag
        self._children: int = 0
        self._text: int = 0

    #@ ensures self._children == \old(self._children) + 1
    #@ assigns self._children
    def append(self, child: int) -> None:
        """Append child element."""
        self._children = self._children + 1

    #@ requires self._children > 0
    #@ ensures self._children == \old(self._children) - 1
    #@ assigns self._children
    def remove(self, child: int) -> None:
        """Remove child element."""
        self._children = self._children - 1

    #@ ensures \result == self._children
    def child_count(self) -> int:
        """Return number of direct children."""
        return self._children

    #@ ensures \result == self._tag
    def get_tag(self) -> int:
        """Return tag identifier."""
        return self._tag

    #@ requires text >= 0
    #@ ensures self._text == text
    #@ assigns self._text
    def set_text(self, text: int) -> None:
        """Set element text content."""
        self._text = text

    #@ ensures \result == self._text
    def get_text(self) -> int:
        """Return text content."""
        return self._text


#@ requires length >= 0
#@ ensures \result >= 0
def parse(length: int) -> int:
    """Parse XML from file. Returns root element tag."""
    return 0


#@ requires length >= 0
#@ ensures \result >= 0
def fromstring(length: int) -> int:
    """Parse XML from string. Returns root element tag."""
    return 0
