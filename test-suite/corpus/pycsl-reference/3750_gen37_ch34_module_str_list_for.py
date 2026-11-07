r"""Test 3750 -- gen #37 ch34 (expected PASS): a module-level list-of-str constant read ONLY as a `for` iterable. It lowered to an opaque `val constant _OPS : int` iterated through `iter_get`, int-typing every element (the honest claim below failed, and a string use of the element was a type error); it now iterates the REAL `seq string` of the literal, exactly like a local str literal. Honest claim must PROVE.
"""
from typing import List

_OPS: List[str] = ["ab", "c", "def"]


#@ ensures \result == 0
#@ assigns \nothing
def has_zz() -> int:
    for op in _OPS:
        if op == "zz":
            return 1
    return 0


#@ ensures \result >= 0
#@ assigns \nothing
def total_len() -> int:
    k = 0
    #@ loop invariant k >= 0
    for op in _OPS:
        k = k + len(op)
    return k
