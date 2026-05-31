"""PyCSL mock for Python's curses.ascii module — Constants and set-membership functions for ASCII characters."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isalnum(c: int) -> int:
    """Mock: Checks for an ASCII alphanumeric character; it is equivalent to ``isalpha(c) or isdigit(c)``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isalpha(c: int) -> int:
    """Mock: Checks for an ASCII alphabetic character; it is equivalent to ``isupper(c) or islower(c)``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isascii(c: int) -> int:
    """Mock: Checks for a character value that fits in the 7-bit ASCII set."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isblank(c: int) -> int:
    """Mock: Checks for an ASCII whitespace character; space or horizontal tab."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def iscntrl(c: int) -> int:
    """Mock: Checks for an ASCII control character (in the range 0x00 to 0x1f or 0x7f)."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isdigit(c: int) -> int:
    """Mock: Checks for an ASCII decimal digit, ``'0'`` through ``'9'``.  This is equivalent to ``c in string.digits``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isgraph(c: int) -> int:
    """Mock: Checks for ASCII any printable character except space."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def islower(c: int) -> int:
    """Mock: Checks for an ASCII lower-case character."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isprint(c: int) -> int:
    """Mock: Checks for any ASCII printable character including space."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ispunct(c: int) -> int:
    """Mock: Checks for any printable ASCII character which is not a space or an alphanumeric character."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isspace(c: int) -> int:
    """Mock: Checks for ASCII white-space characters; space, line feed, carriage return, form feed, horizontal tab, vertical tab."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isupper(c: int) -> int:
    """Mock: Checks for an ASCII uppercase letter."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isxdigit(c: int) -> int:
    """Mock: Checks for an ASCII hexadecimal digit.  This is equivalent to ``c in string.hexdigits``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isctrl(c: int) -> int:
    """Mock: Checks for an ASCII control character (ordinal values 0 to 31)."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismeta(c: int) -> int:
    """Mock: Checks for a non-ASCII character (ordinal values 0x80 and above)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ascii(c: int) -> int:
    """Mock: Return the ASCII value corresponding to the low 7 bits of *c*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ctrl(c: int) -> int:
    """Mock: Return the control character corresponding to the given character (the character bit value is bitwise-anded with 0x1f)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def alt(c: int) -> int:
    """Mock: Return the 8-bit character corresponding to the given ASCII character (the character bit value is bitwise-ored with 0x80..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unctrl(c: int) -> int:
    """Mock: Return a string representation of the ASCII character *c*.  If *c* is printable, this string is the character itself.  I..."""
    return 0
