"""Runtime gate CR1 — cast returns v unchanged for any value type.

Spec clause CR1 (cast-twoplane-spec.md §2): `cast(t, v)` returns `v`
unchanged at runtime. Per S3 the typing library documents `cast` as "return
`v` unchanged" — pure identity — and S4 (CPython `Lib/typing.py`)
implements it literally as `def cast(typ, val): return val`. The shim
carries only `ensures \\result == val` and performs NO type check, NO
conversion, NO narrowing, NO validation of any kind. Identity must
discharge for ANY value type (int, str, None).

This driver calls the `cast` shim directly with an int, a str, and None,
expecting the identity postcondition to discharge for all three.

Expected (from spec): PASS — identity discharges regardless of value type.
"""

from pycsl_lib.typ import cast


#@ ensures \result == val
def call_int(val) -> int:
    return cast(int, val)


#@ ensures \result == val
def call_str(val) -> int:
    return cast(str, val)


#@ ensures \result == val
def call_none(val) -> int:
    return cast(type(None), val)


if __name__ == "__main__":
    assert call_int(5) == 5
    assert call_str("hello") == "hello"
    assert call_none(None) is None
    print("PASS")
