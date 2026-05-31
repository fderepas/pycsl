"""PyCSL mock for Python's email.iterators module — Iterate over a  message object tree."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def body_line_iterator(msg: int, decode: int) -> int:
    """Mock: This iterates over all the payloads in all the subparts of *msg*, returning the string payloads line-by-line.  It skips ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def typed_subpart_iterator(msg: int, maintype: int, subtype: int) -> int:
    """Mock: This iterates over all the subparts of *msg*, returning only those subparts that match the MIME type specified by *maint..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _structure(msg: int, fp: int, level: int, include_default: int) -> int:
    """Mock: Prints an indented representation of the content types of the message object structure.  For example: .. testsetup:: imp..."""
    return 0
