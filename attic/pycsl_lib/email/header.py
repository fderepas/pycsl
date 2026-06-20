"""PyCSL mock for Python's email.header module — Representing non-ASCII headers."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def decode_header(header: int) -> int:
    """Mock: Decode a message header value without converting the character set. The header value is in *header*. For historical reas..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def make_header(decoded_seq: int, maxlinelen: int, header_name: int, continuation_ws: int) -> int:
    """Mock: Create a :class:`Header` instance from a sequence of pairs as returned by :func:`decode_header`. :func:`decode_header` t..."""
    return 0
