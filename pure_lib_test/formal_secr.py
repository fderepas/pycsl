# Formal tests for pure_lib/secr — secrets module
from pure_lib.secr import randbelow, token_bytes, token_hex, compare_digest


#@ requires n > 0
#@ ensures \result >= 0
def test_randbelow_nonneg(n: int) -> int:
    """randbelow returns non-negative."""
    return randbelow(n)


#@ requires nbytes > 0
#@ ensures \result >= 0
def test_token_bytes_nonneg(nbytes: int) -> int:
    """token_bytes returns non-negative length."""
    return token_bytes(nbytes)


#@ requires nbytes > 0
#@ ensures \result >= 0
def test_token_hex_nonneg(nbytes: int) -> int:
    """token_hex returns non-negative."""
    return token_hex(nbytes)


#@ requires a >= 0
#@ ensures \result >= 0
def test_compare_digest_nonneg(a: int) -> int:
    """compare_digest returns non-negative."""
    return compare_digest(a, a)
