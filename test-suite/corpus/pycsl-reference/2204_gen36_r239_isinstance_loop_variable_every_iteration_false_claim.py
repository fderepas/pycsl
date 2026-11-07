r"""Test 2204 — route #239 (expected FAIL): the loop variable across iterations. `v = xs[i]` is
rebound every iteration, but the tag was `typeof_op 118` (the name `v`), so the invariant
`i > 0 ==> (first == 1 <==> isinstance(v, int))` was preserved by a constant and
`\result == 1` ("every element has the first element's type") PROVED at f926a808 while
CPython `f([1, "s"])` = 0. Now the invariant is about `typeof_op !v` and is not preserved.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ ensures \result == 1
#@ assigns \nothing
def f(xs: List[Any]) -> int:
    i = 0
    first = 0
    same = 1
    #@ loop invariant 0 <= i <= len(xs)
    #@ loop invariant same == 1
    #@ loop invariant first == 0 or first == 1
    #@ loop invariant i > 0 ==> (first == 1 <==> isinstance(v, int))
    #@ loop variant len(xs) - i
    while i < len(xs):
        v = xs[i]
        k = 0
        if isinstance(v, int):
            k = 1
        if i == 0:
            first = k
        elif first != k:
            same = 0
        i += 1
    return same
