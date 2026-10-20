r"""Test 3351 -- route #291 (expected PASS): CONTROLS: an exact int keeps its value-keyed rendering (`f"{len(xs)}" == f"{1}"`), a non-empty spec renders a bool as its int (`f"{b:>5}" == f"{x:>5}"`, CPython '    1' both), and the same formatted operand twice is equal.
"""
# pycsl-expected: PASS
from typing import List


#@ requires \length(xs) == 1
#@ ensures \result == True
def exact_int(xs: List[int]) -> bool:
    return f"{len(xs)}" == f"{1}"


#@ ensures \result == True
def spec_formats_bool_as_int() -> bool:
    b = True
    x = 1
    return f"{b:>5}" == f"{x:>5}"


#@ ensures \result == True
def same_operand(n: int) -> bool:
    return f"{n:>5}" == f"{n:>5}"


if __name__ == "__main__":
    assert exact_int([7]) is True
    assert spec_formats_bool_as_int() is True
    assert same_operand(3) is True
