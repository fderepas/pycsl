# Formal tests for pycsl_lib/rng — random
from pycsl_lib.rng import randint, randrange, sample_len


#@ requires a >= 0
#@ requires b >= a
#@ ensures \result >= a
#@ ensures \result <= b
def test_randint_range(a: int, b: int) -> int:
    """randint result in [a, b]."""
    return randint(a, b)


#@ requires start >= 0
#@ requires stop > start
#@ ensures \result >= start
#@ ensures \result < stop
def test_randrange_range(start: int, stop: int) -> int:
    """randrange result in [start, stop)."""
    return randrange(start, stop)


#@ requires \length(seq) > 0
#@ requires k >= 0
#@ requires k <= \length(seq)
#@ ensures \result == k
def test_sample_exact_len(seq: list, k: int) -> int:
    """sample returns exactly k elements."""
    return sample_len(seq, k)
