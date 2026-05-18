"""Test 0199 - PyCSL Annotation Reference 1.1 (dict type support)"""
_ = 0  # anchor
#@ requires \length(d) >= 10
#@ ensures \result == d[0] + d[1]
def sum_first_two(d: dict, n: int) -> int:
    """Sum the first two entries of a dict-like mapping."""
    return d[0] + d[1]
