# Formal tests for pycsl_lib/secr — secrets module
from pycsl_lib.secr import randbelow, token_hex, compare_digest


#@ requires n > 0
#@ ensures \result >= 0
def test_randbelow_nonneg(n: int) -> int:
    """randbelow returns non-negative."""
    return randbelow(n)


#@ requires nbytes > 0
def test_token_hex_returns_str(nbytes: int) -> str:
    """token_hex returns a string."""
    return token_hex(nbytes)


#@ requires a >= 0
#@ ensures \result >= 0
def test_compare_digest_nonneg(a: int) -> int:
    """compare_digest returns non-negative."""
    return compare_digest(a, a)
