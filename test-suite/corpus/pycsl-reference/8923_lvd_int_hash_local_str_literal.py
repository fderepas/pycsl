r"""Test 8923 -- lvD string literal into an int-hash local (expected PASS): the `visit_MatchStar` shape.
`name` is first bound to an unannotated (int-model) value, so it is pre-declared `ref 0`, an int-HASH
slot; `name = "_"` lowers to the literal's `stable_hash` (the A7 collapse every call argument already
uses), and `f"*{name}"` is the `str_concat_op "*" (int_to_string !name)` string, never empty. At
base the assignment was `name := "_"` against `ref 0`, a Why3 type error. Twins: 8924, 8925 (FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ ensures \result != ""
#@ assigns \nothing
def star(x) -> str:
    name = x
    if name is None:
        name = "_"
    return f"*{name}"


if __name__ == "__main__":
    r = star(None)
    print("VIOLATION contract" if r == "" else "result", r)
