# Formal tests for pure_lib/sock — socket module
from pure_lib.sock import AF_INET, SOCK_STREAM


#@ ensures \result == 2
def test_af_inet() -> int:
    """AF_INET is 2."""
    return AF_INET


#@ ensures \result == 1
def test_sock_stream() -> int:
    """SOCK_STREAM is 1."""
    return SOCK_STREAM
