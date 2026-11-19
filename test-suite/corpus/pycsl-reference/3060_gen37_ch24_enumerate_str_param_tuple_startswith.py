r"""Test 3060 — gen #37 ch24 (expected PASS): `for i, line in enumerate(xs)` over a FORMAL
`List[str]` param, and `s.startswith((p1, p2))` with a TUPLE of prefixes (the shape of the
emitter's own `abstract_ops._find_abstract_val_insert_idx`). At base the enumerate fell to the
opaque `enumerate_1 xs : int` (L3-tc: `array string` vs `int`) and the tuple test to the
opaque polymorphic `startswith_2` (result unconstrained). Now the loop binds `i = !idx` and
`line = xs[!idx]` (a real `string`) over `Array.length xs`, and the tuple test is the
disjunction of the faithful `str_startswith_op` per prefix. Twins: 3061, 3062 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures -1 <= \result and \result < \length(xs)
#@ assigns \nothing
def last_decl(xs: List[str], tag: str) -> int:
    r = -1
    #@ loop invariant -1 <= r and r < \length(xs)
    for i, line in enumerate(xs):
        if line.startswith((tag, "val ")):
            r = i
    return r


#@ requires s == "val x"
#@ ensures \result == 1
#@ assigns \nothing
def is_decl(s: str) -> int:
    if s.startswith(("type ", "val ")):
        return 1
    return 0


if __name__ == "__main__":
    assert last_decl(["let a", "type t", "val v", "x"], "type ") == 2
    assert last_decl([], "type ") == -1
    assert is_decl("val x") == 1
    print("ok")
