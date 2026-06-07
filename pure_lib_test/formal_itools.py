# Formal tests for pure_lib/itools — itertools module
from pure_lib.itools import count_n, repeat_n, chain_len, islice_len


#@ requires n >= 0
#@ ensures \result == n
def test_count_n_exact(n: int) -> int:
    """count_n produces exactly n items."""
    return count_n(0, n)


#@ requires n >= 0
#@ ensures \result == n
def test_repeat_n_exact(n: int) -> int:
    """repeat produces exactly n items."""
    return repeat_n(42, n)


#@ requires \length(a) >= 0
#@ requires \length(b) >= 0
#@ ensures \result == \length(a) + \length(b)
def test_chain_additive(a: list, b: list) -> int:
    """chain length is sum of input lengths."""
    return chain_len(a, b)


#@ requires \length(seq) >= 0
#@ requires start >= 0
#@ requires stop >= start
#@ requires stop <= \length(seq)
#@ ensures \result == stop - start
def test_islice_exact(seq: list, start: int, stop: int) -> int:
    """islice yields exactly stop - start elements."""
    return islice_len(seq, start, stop)
