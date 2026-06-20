"""PyCSL mock for Python's hmac module — Keyed-Hashing for Message Authentication (HMAC) implementation."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def new(key: int, msg: int, digestmod: int) -> int:
    """Mock: Return a new hmac object.  *key* is a bytes or bytearray object giving the secret key.  If *msg* is present, the method ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def digest(key: int, msg: int, digest: int) -> int:
    """Mock: Return digest of *msg* for given secret *key* and *digest*. The function is equivalent to ``HMAC(key, msg, digest).diges..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compare_digest(a: int, b: int) -> int:
    """Mock: Return ``a == b``.  This function uses an approach designed to prevent timing analysis by avoiding content-based short c..."""
    return 0
