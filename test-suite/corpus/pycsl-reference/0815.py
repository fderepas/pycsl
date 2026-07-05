"""Test 0815 — WL-03 regression lock (POSITIVE): a fixed-length `Tuple[T1, ..., Tn]`
PARAMETER gets the faithful per-slot model, so a slot read `t[i]` reads the true
slot type, not the opaque `int` collapse.

Before the fix, a `Tuple[...]`-annotated parameter collapsed to a bare `int` with
an opaque `subscript_get (x:int)(i:int):int`, so a MIXED `Tuple[int, str]` param's
`t[1]` (a str) read back an int — TYPEERR at a `str` use site — and a homogeneous
`Tuple[int, int]` param's `t[0]` was content-opaque (UNPROVABLE). PyCSL now
synthesizes a per-slot record `type pytuple_int_str = { field0: int; field1: string }`
and lowers `t[i]` to the i-th record field, so the mixed `t[1] : string` and the
homogeneous `t[0] : int` are BOTH faithfully typed and provable.

Ground truth: for a tuple `t`, `t[i]` is the i-th component at its own declared
type; the components are independent. Twin: 0816 (# pycsl-expected: FAIL) asserts a
FALSE slot-content claim (t[1] equals a wrong slot), which must NOT be provable.
"""
_ = 0  # anchor
from typing import Tuple


#@ ensures \result == t[1]
def snd_str(t: Tuple[int, str]) -> str:
    """Mixed tuple: the second slot is a STRING (was an opaque int -> TYPEERR)."""
    return t[1]


#@ ensures \result == t[0]
def fst_int(t: Tuple[int, str]) -> int:
    """Mixed tuple: the first slot is an INT, distinct from the string slot."""
    return t[0]


#@ ensures \result == t[0]
def ii_fst(t: Tuple[int, int]) -> int:
    """Homogeneous tuple: `t[0]` is content-provable (was opaque subscript_get)."""
    return t[0]


#@ ensures \result == t[1]
def ii_snd(t: Tuple[int, int]) -> int:
    """Homogeneous tuple: `t[1]` reads the SECOND slot, independent of `t[0]`."""
    return t[1]


if __name__ == "__main__":
    assert snd_str((7, "hi")) == "hi"
    assert fst_int((7, "hi")) == 7
    assert ii_fst((3, 4)) == 3
    assert ii_snd((3, 4)) == 4
