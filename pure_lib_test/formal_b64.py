# Formal tests for pure_lib/b64 — base64 module
from pure_lib.b64 import b64encode_len, b64decode_len, b16encode_len, b16decode_len, b32encode_len


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ ensures n > 0 ==> \result >= 4
def test_b64encode_properties(n: int) -> int:
    """Base64 encoding: empty -> empty, non-empty -> at least 4."""
    return b64encode_len(n)


#@ requires n >= 0
#@ requires n % 4 == 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
def test_b64decode_nonneg(n: int) -> int:
    """Base64 decoding: non-negative output length."""
    return b64decode_len(n)


#@ requires n >= 0
#@ ensures \result == n * 2
def test_b16encode_exact(n: int) -> int:
    """Base16 encoding doubles the length."""
    return b16encode_len(n)


#@ requires n >= 0
#@ requires n % 2 == 0
#@ ensures \result == n // 2
def test_b16decode_exact(n: int) -> int:
    """Base16 decoding halves the length."""
    return b16decode_len(n)


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
def test_b32encode_nonneg(n: int) -> int:
    """Base32 encoding: non-negative output."""
    return b32encode_len(n)
