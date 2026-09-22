r"""Test 1699 - ROUTE #201 carrier (gen #30): a STRING LITERAL actual reaching a parameter DECLARED `List[int]` fell through `_array_coerce_arg`'s TAIL to `(Array.make 1 0)` - an array whose length the model KNOWS to be 1. Route #193 repaired the `stripped == "0"` case of that same function for exactly this reason and LEFT THE TAIL: a string literal reaches it because it is neither `"0"`, nor array-shaped, nor alphanumeric once the quotes are counted. The callee's contract is TRUE OF ITS OWN BODY and READS the length, so `callee("ab")` emitted `(callee (Array.make 1 0))` and PROVED `\result == 1` while CPython answers 2 (`len("ab")` is 2); the TRUE twin was REFUSED. The tail now answers `(any (array int))`, which stands for EVERY array of ints. This file must FAIL.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ requires True
#@ ensures len(p) == 1 ==> \result == 1
#@ ensures len(p) != 1 ==> \result == 2
def callee(p: List[int]) -> int:
    if len(p) == 1:
        return 1
    return 2


#@ ensures \result == 1
def probe() -> int:
    return callee("ab")
