"""Test 0583 — inline a method taking an `array int` param; read an element (arity2.md 2a).

`run` calls `rd.at(a, i)` on the module global `rd`. The call is INLINED: `at`'s body
`return a[i]` is spliced with self→rd, and the array param `a` flows through unchanged. The
caller then proves `\result == a[i]` directly. Companion to the mutation case `0585`; this
shape already verified before the 2b fix (array-param read needs no operation re-selection),
so it guards 2a (declaration typing) against regression.
"""
# pycsl-flags: --memory-model hoare


class Reader:
    def __init__(self) -> None:
        pass

    #@ requires \valid(a, 4)
    #@ requires 0 <= i and i < 4
    #@ ensures \result == a[i]
    #@ assigns \nothing
    def at(self, a: list, i: int) -> int:
        return a[i]


rd = Reader()


#@ requires \valid(a, 4)
#@ requires 0 <= i and i < 4
#@ ensures \result == a[i]
#@ assigns \nothing
def run(a: list, i: int) -> int:
    return rd.at(a, i)
