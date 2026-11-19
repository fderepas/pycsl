r"""Test 9004 -- lvF cap-trusted-val-unit-return (expected PASS): the promotion leaves a `-> None`
`\trusted` stub a `unit` `val` (a procedure), so a statement call to it is still `let _ = .. in ()`-free
plain sequencing and a caller proves its own postcondition. Control for 9000: the declared annotation,
not the `pass` body, decides the `val`'s return type.
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ \trusted reviewer: lvF
#@ assigns \nothing
def log(k: int) -> None:
    pass


#@ ensures \result == 2 * k
#@ assigns \nothing
def twice(k: int) -> int:
    log(k)
    return 2 * k


if __name__ == "__main__":
    r = twice(3)
    print("VIOLATION contract" if r != 6 else "result", r)
