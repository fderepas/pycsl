"""PyCSL mock for Python's email.encoders module — Encoders for email message payloads."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def encode_quopri(msg: int) -> int:
    """Mock: Encodes the payload into quoted-printable form and sets the :mailheader:`Content-Transfer-Encoding` header to ``quoted-p..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def encode_base64(msg: int) -> int:
    """Mock: Encodes the payload into base64 form and sets the :mailheader:`Content-Transfer-Encoding` header to ``base64``.  This is..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def encode_7or8bit(msg: int) -> int:
    """Mock: This doesn't actually modify the message's payload, but it does set the :mailheader:`Content-Transfer-Encoding` header t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def encode_noop(msg: int) -> int:
    """Mock: This does nothing; it doesn't even set the :mailheader:`Content-Transfer-Encoding` header."""
    return 0
