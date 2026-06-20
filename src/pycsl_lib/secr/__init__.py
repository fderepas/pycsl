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
#@ assigns \nothing
def token_bytes(nbytes: int) -> str:
    """Return nbytes random bytes as a bytes-like string."""
    return ""


#@ requires nbytes > 0
#@ assigns \nothing
def token_hex(nbytes: int) -> str:
    """Return random hex string (2*nbytes chars)."""
    return ""


#@ requires nbytes > 0
#@ assigns \nothing
def token_urlsafe(nbytes: int) -> str:
    """Return URL-safe base64 token string."""
    return ""


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def compare_digest(a: int, b: int) -> int:
    """Constant-time comparison. Returns 1 if equal, 0 otherwise."""
    if a == b:
        return 1
    return 0
