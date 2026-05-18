"""Test 0233 — Library stubs (functools, itertools)"""
_ = 0  # anchor
from functools import reduce
from itertools import chain

#@ requires x >= 0
#@ ensures \result >= 0
def test_with_imports(x: int) -> int:
    return x

if __name__ == "__main__":
    assert test_with_imports(5) == 5
