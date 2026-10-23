"""Test 0986 — reassigning an array LOCAL from a non-literal right-hand side is REFUSED.
It used to be a NO-OP, and the code said so.

`_emit_array_local_reassign` handles only an `ArrayLit` RHS. Its docstring said of the
rest: "other shapes (method calls etc.) fall through to a no-op (soundness depends on the
caller treating the array as opaque after this point — typically handled by `\trusted`
upstream)". The local is NOT opaque afterwards: it keeps its OLD value, and every later
read is answered from it. Measured, before this refusal:

    #@ ensures \length(\result) == 2 and \result[0] == 9
    def g() -> List[int]:
        return [9, 9]

    #@ ensures \result == 1                       <-- FALSE OF THE PROGRAM
    def f() -> int:
        xs: List[int] = [1, 2]
        xs = g()
        return xs[0]

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 9. Test 0987 is the sharper half of the same route.

REFUSED rather than modelled: assigning a non-literal sequence to an array-local means
REBINDING the name to another array, and the array-local representation — a fixed
`Array.make N 0` plus a separate `<name>_len` counter, not a `ref` — cannot be rebound.
The faithful lowering needs the local promoted to a `ref (array int)`, which is the same
value-model capability routes #13 and #17 need.

CENSUS: corpus emission BYTE-IDENTICAL across all 820 files, mirror L3-tc 53/53,
`src/pycsl_lib` unchanged.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \length(\result) == 2 and \result[0] == 9
#@ assigns \nothing
def g() -> List[int]:
    return [9, 9]


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    xs = g()
    return xs[0]
