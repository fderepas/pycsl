# pure_lib/htmlm — pure-Python html module model
# Named 'htmlm' to avoid stdlib name clash.
#
# Contracts derived from library_reference/html.rst.
# RST: "Convert the characters &, <, > to HTML-safe sequences."
# RST: "Convert all named and numeric character references to Unicode."


#@ requires s >= 0
#@ ensures \result >= s
def escape(s: int) -> int:
    """Escape &, <, >, quote chars for HTML.
    RST: 'Convert &, <, > to HTML-safe sequences.' Each replacement
    grows the string (& → &amp; is 4 extra chars), so result >= input."""
    return s


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result <= s
def unescape(s: int) -> int:
    """Unescape HTML entities back to characters.
    RST: 'Convert all named and numeric character references to
    corresponding Unicode characters.' Entity refs are longer than the
    chars they represent, so result <= input."""
    return s


#@ requires s >= 0
#@ ensures \result >= s
def escape_quote(s: int) -> int:
    """Escape including quote chars (quote=True mode).
    RST: 'the characters \" and ' are also translated.'
    Same growth property as escape: result >= input."""
    return s
