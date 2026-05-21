"""PyCSL mock for Python's secrets module — Generate secure random numbers for managing secrets."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def choice(seq: int) -> int:
    """Mock: Return a randomly chosen element from a non-empty sequence."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def randbelow(exclusive_upper_bound: int) -> int:
    """Mock: Return a random int in the range [0, *exclusive_upper_bound*)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def randbits(k: int) -> int:
    """Mock: Return a non-negative int with *k* random bits."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def token_bytes(nbytes: int) -> int:
    """Mock: Return a random byte string containing *nbytes* number of bytes. If *nbytes* is not specified or ``None``, :const:`DEFAU..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def token_hex(nbytes: int) -> int:
    """Mock: Return a random text string, in hexadecimal.  The string has *nbytes* random bytes, each byte converted to two hex digit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def token_urlsafe(nbytes: int) -> int:
    """Mock: Return a random URL-safe text string, containing *nbytes* random bytes.  The text is Base64 encoded, so on average each ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def compare_digest(a: int, b: int) -> int:
    """Mock: Return ``True`` if strings or :term:`bytes-like objects <bytes-like object>` *a* and *b* are equal, otherwise ``False``,..."""
    return 0
