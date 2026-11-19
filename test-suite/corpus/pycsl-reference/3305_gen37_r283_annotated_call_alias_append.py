r"""Test 3305 -- route #283 (expected FAIL): census: an ANNOTATED local is seq-promoted and bound as `ref (snapshot (ident a))` -- a COPY -- so `len(a) == 1` PROVED after `b.append(1)`; CPython: 2.
Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0]
    b: List[int] = ident(a)
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
