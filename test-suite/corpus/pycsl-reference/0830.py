"""Test 0830 — WL-04b regression lock (POSITIVE, List[Tuple[int, str]]): a FLAT
`List[Tuple[int, str]]` PARAMETER realizes its element as the synthesized per-slot
record (`array pytuple_int_str`), so a slot read `a[i][1]` is a native record-field
projection at the FAITHFUL slot type — not the opaque `subscript_get` collapse.

Before the fix, a `List[Tuple[int, str]]` param with `a[i][1]` was hijacked into the
rectangular `matrix int` model (a matrix cell, losing the per-slot type) or collapsed
through `subscript_get a[i] 1` (an int at a `str` use site — TYPEERR). PyCSL now reuses
the WL-03 per-slot record `pytuple_int_str = { field0: int; field1: string }` as the
list ELEMENT (`array pytuple_int_str`; the record is emitted PURE for the array
element position), so `a[i]` reads the tuple record and `a[i][k]` projects the k-th
slot at its own type — `a[i][0] : int`, `a[i][1] : str`.

Ground truth: for a list `a` of `(int, str)` pairs, `a[i][0]` and `a[i][1]` are the
i-th pair's independent slots at distinct types. Twin: 0831 (# pycsl-expected: FAIL)
covers the false cross-field claim for the dataclass variant.
"""
_ = 0  # anchor
from typing import List, Tuple


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i][1]
def snd(a: List[Tuple[int, str]], i: int) -> str:
    """The SECOND slot of the i-th tuple is a `str` (was an int -> TYPEERR)."""
    return a[i][1]


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i][0]
def fst(a: List[Tuple[int, str]], i: int) -> int:
    """The FIRST slot of the i-th tuple is an `int`, independent of the second."""
    return a[i][0]


if __name__ == "__main__":
    pairs = [(1, "a"), (2, "b"), (3, "c")]
    assert snd(pairs, 2) == "c"
    assert fst(pairs, 0) == 1
