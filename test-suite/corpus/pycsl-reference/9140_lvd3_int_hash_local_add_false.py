r"""Test 9140 -- lvD3 (rt54 R54-F4, expected FAIL): `name = x; name = "abc"; name + 1` with `x: int` under
`no_exception`. CPython raises TypeError (str + int). lvD C2 lowered the literal to its int stable_hash and the
int `+` proved; lvD3 keeps C2 only for a local read solely as an f-string part / `is None` operand, so here
the assignment is the ill-typed `name := "abc"` against `ref 0` (fail-closed). Twins 9141-9149.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    name = x
    name = "abc"
    return name + 1


if __name__ == "__main__":
    try:
        print("result", f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
