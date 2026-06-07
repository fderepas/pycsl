# Formal tests for pure_lib/tok — tokenize module
from pure_lib.tok import detect_encoding, generate_tokens


#@ requires readline >= 0
#@ ensures \result >= 0
def test_detect_encoding_nonneg(readline: int) -> int:
    """detect_encoding returns non-negative."""
    return detect_encoding(readline)


#@ requires readline >= 0
#@ ensures \result >= 0
def test_generate_tokens_nonneg(readline: int) -> int:
    """generate_tokens returns non-negative."""
    return generate_tokens(readline)
