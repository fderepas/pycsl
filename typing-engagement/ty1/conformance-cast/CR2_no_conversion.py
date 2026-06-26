"""Runtime gate CR2 — cast performs NO conversion (identity, not coercion).

Spec clause CR2 (cast-twoplane-spec.md §2 — no conversion): `cast(t, v)`
returns `v` UNCHANGED — it does NOT convert `v` to type `t`. The sharpest
test is `cast(int, "hello")`: a shim that CONVERTED would return an int
(coercing "hello" to int raises ValueError at runtime in CPython; a
hypothetical converting shim would either raise or return a converted
value). The faithful shim returns "hello" unchanged — a string — and the
identity postcondition `\\result == "hello"` discharges with the ORIGINAL
value, NOT with a converted int.

This is the runtime-plane honesty probe: cast must NOT convert. The
identity postcondition discharges with the original (string) value.

Expected (from spec): PASS — `cast(int, "hello")` returns "hello"
unchanged; the identity postcondition holds with the original value.
"""

from pycsl_lib.typ import cast


#@ ensures \result == val
def cast_int_on_string(val) -> int:
    return cast(int, val)


if __name__ == "__main__":
    assert cast_int_on_string("hello") == "hello"
    # CR2 negative observation: a converting cast would have raised
    # ValueError or returned an int; neither happens — the original
    # string is returned unchanged.
    assert type(cast_int_on_string("hello")) == str
    print("PASS")
