"""PyCSL mock for Python's html module — Helpers for manipulating HTML."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/html.html#html.escape
#@ ensures \result >= 0
def escape(s: int, quote: int) -> int:
    """Mock: Convert the characters ``&``, ``<`` and ``>`` in string *s* to HTML-safe sequences.  Use this if you need to display tex..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/html.html#html.unescape
#@ ensures len(\result) <= len(s)
def unescape(s: int) -> int:
    """Mock: Convert all named and numeric character references (e.g. ``&gt;``, ``&#62;``, ``&#x3e;``) in the string *s* to the corre..."""
    return 0
