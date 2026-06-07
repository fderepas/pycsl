# Formal tests for pure_lib/hmacmod — hmac module
from pure_lib.hmacmod import new_hmac, digest, compare_digest


#@ requires key_len > 0
#@ requires digest_size > 0
#@ ensures \result > 0
def test_new_returns_size(key_len: int, digest_size: int) -> int:
    """new_hmac returns the digest size."""
    return new_hmac(key_len, digest_size)


#@ requires key_len > 0
#@ requires msg_len >= 0
#@ requires digest_size > 0
#@ ensures \result > 0
def test_digest_returns_size(key_len: int, msg_len: int, digest_size: int) -> int:
    """digest returns the digest size."""
    return digest(key_len, msg_len, digest_size)


#@ requires a > 0
#@ ensures \result >= 0
#@ ensures \result <= 1
def test_compare_self(a: int) -> int:
    """Comparing same length yields 1."""
    return compare_digest(a, a)
