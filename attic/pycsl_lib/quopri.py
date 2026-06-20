"""PyCSL mock for Python's quopri module — Encode and decode files using the MIME quoted-printable encoding."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def decode(input: int, output: int, header: int) -> int:
    """Mock: Decode the contents of the *input* file and write the resulting decoded binary data to the *output* file. *input* and *o..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def encode(input: int, output: int, quotetabs: int, header: int) -> int:
    """Mock: Encode the contents of the *input* file and write the resulting quoted-printable data to the *output* file. *input* and ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decodestring(s: int, header: int) -> int:
    """Mock: Like :func:`decode`, except that it accepts a source :class:`bytes` and returns the corresponding decoded :class:`bytes`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def encodestring(s: int, quotetabs: int, header: int) -> int:
    """Mock: Like :func:`encode`, except that it accepts a source :class:`bytes` and returns the corresponding encoded :class:`bytes`..."""
    return 0
