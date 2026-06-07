# pure_lib/htmlm — pure-Python html module model
# Named 'htmlm' to avoid stdlib name clash.
#
# Contracts derived from library_reference/html.rst.
# RST: "Convert the characters &, <, > to HTML-safe sequences."
# RST: "Convert all named and numeric character references to Unicode."
# RST: "HTMLParser — parse HTML and XHTML documents."


#@ requires s >= 0
#@ ensures \result >= s
#@ ensures s == 0 ==> \result == 0
def escape(s: int) -> int:
    """Escape &, <, >, quote chars for HTML.
    RST: 'Convert &, <, > to HTML-safe sequences.' Each replacement
    grows the string (& → &amp; is 4 extra chars), so result >= input."""
    return s


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result <= s
#@ ensures s == 0 ==> \result == 0
def unescape(s: int) -> int:
    """Unescape HTML entities back to characters.
    RST: 'Convert all named and numeric character references to
    corresponding Unicode characters.' Entity refs are longer than the
    chars they represent, so result <= input."""
    return s


#@ requires s >= 0
#@ ensures \result >= s
#@ ensures s == 0 ==> \result == 0
def escape_quote(s: int) -> int:
    """Escape including quote chars (quote=True mode).
    RST: 'the characters " and ' are also translated.'
    Same growth property as escape: result >= input."""
    return s


# --- HTMLParser class ---

""  # pycsl
#@ class invariant self._line >= 1
#@ class invariant self._col >= 0
#@ class invariant self._offset >= 0
class HTMLParser:
    """RST: 'Create a new HTMLParser instance. An HTMLParser instance is
    fed HTML data and calls handler methods when start tags, end tags,
    text, comments, and other markup elements are encountered.'"""

    def __init__(self):
        self._line = 1
        self._col = 0
        self._offset = 0

    #@ requires n >= 0
    #@ ensures self._offset == \old(self._offset) + n
    #@ assigns self._offset
    def feed(self, n: int) -> None:
        """RST: 'Feed some text to the parser.' Advances offset by data length."""
        self._offset = self._offset + n

    #@ ensures \result == self._line
    #@ assigns \nothing
    def getpos_line(self) -> int:
        """RST: 'Return source line number.' Part of getpos() tuple."""
        return self._line

    #@ ensures \result == self._col
    #@ assigns \nothing
    def getpos_col(self) -> int:
        """RST: 'Return source column offset.' Part of getpos() tuple."""
        return self._col

    #@ ensures self._offset == 0
    #@ ensures self._line == 1
    #@ ensures self._col == 0
    #@ assigns self._offset, self._line, self._col
    def reset(self) -> None:
        """RST: 'Reset the instance. Loses all unprocessed data.'"""
        self._offset = 0
        self._line = 1
        self._col = 0
