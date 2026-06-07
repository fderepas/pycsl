# Pure model for secrets — secure random number generation
# Models as non-deterministic bounded functions.


#@ requires n > 0
#@ ensures \result >= 0
#@ ensures \result < n
def randbelow(n: int) -> int:
    """Return random int in [0, n)."""
    return 0


#@ requires k > 0
#@ ensures \result >= 0
def randbits(k: int) -> int:
    """Return non-negative int with k random bits."""
    return 0


#@ requires size > 0
#@ ensures \result >= 0
#@ ensures \result < size
def choice(size: int) -> int:
    """Return random index from sequence of given size."""
    return 0


#@ requires nbytes > 0
#@ ensures \result == nbytes
def token_bytes(nbytes: int) -> int:
    """Return nbytes random bytes (modeled as length)."""
    return nbytes


#@ requires nbytes > 0
#@ ensures \result == nbytes * 2
def token_hex(nbytes: int) -> int:
    """Return hex string of nbytes random bytes (length = 2*nbytes)."""
    return nbytes * 2


#@ requires nbytes > 0
#@ ensures \result >= nbytes
def token_urlsafe(nbytes: int) -> int:
    """Return URL-safe base64 token (length >= nbytes)."""
    return nbytes


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def compare_digest(a: int, b: int) -> int:
    """Constant-time comparison. Returns 1 if equal, 0 otherwise."""
    if a == b:
        return 1
    return 0
