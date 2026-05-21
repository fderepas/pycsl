"""PyCSL mock for Python's email.parser module — Parse flat text email messages to produce a message object structure."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def message_from_bytes(s: int, _class: int, policy: int) -> int:
    """Mock: Return a message object structure from a :term:`bytes-like object`.  This is equivalent to ``BytesParser().parsebytes(s)..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def message_from_binary_file(fp: int, _class: int, __policy: int) -> int:
    """Mock: Return a message object structure tree from an open binary :term:`file object`.  This is equivalent to ``BytesParser().p..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def message_from_string(s: int, _class: int, policy: int) -> int:
    """Mock: Return a message object structure from a string.  This is equivalent to ``Parser().parsestr(s)``.  *_class* and *policy*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def message_from_file(fp: int, _class: int, policy: int) -> int:
    """Mock: Return a message object structure tree from an open :term:`file object`. This is equivalent to ``Parser().parse(fp)``.  ..."""
    return 0
