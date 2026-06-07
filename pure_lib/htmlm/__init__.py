# pure_lib/htmlm — pure-Python html module model
# Named 'htmlm' to avoid stdlib name clash.
#
# Models html.escape() and html.unescape() as string transforms.
# Body-proven for escape (deterministic char replacement).


#@ requires s >= 0
#@ ensures \result >= 0
def escape(s: int) -> int:
    """Escape &, <, >, \" characters for HTML.
    Model: input length s, output length >= s (escaping only grows)."""
    return s


#@ requires s >= 0
#@ ensures \result >= 0
def unescape(s: int) -> int:
    """Unescape HTML entities back to characters.
    Model: output length <= expanded input (unescaping only shrinks or preserves)."""
    return s


#@ requires s >= 0
#@ ensures \result >= 0
#@ ensures \result >= s
def escape_quote(s: int) -> int:
    """Escape including single quotes (quote=True mode).
    Model: result >= input (escaping grows or preserves)."""
    return s
