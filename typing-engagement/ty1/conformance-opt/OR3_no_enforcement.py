"""Runtime gate OR3 — no enforcement (the Optional shim is identity).

Spec clause OR3 (optional-twoplane-spec.md §2.1): the runtime does NOT
check that a value stored under an `Optional[X]` annotation is `None` or
of type `X`. The Optional shim (via the Union seam) is identity — it
discharges for ANY value, regardless of arm membership. This is the
specialization of Union R3.

Per the §12.4 surface, `Optional[X]` reuses the `Union` shim
(`src/pycsl_lib/typ/__init__.py`) — there is NO distinct `Optional`
runtime class (OR1/OR8). So this driver exercises the same `Union`
shim, calling it with values that are NOT in any arm of any declared
Optional (a string, a list, None) and expects the identity
postcondition to discharge regardless (R8 forbids the shim from
validating arm membership).

Expected (from spec): prove the identity postcondition for every call.
"""

from pycsl_lib.typ import Union


#@ ensures \result == val
def call_string(val) -> int:
    return Union(int, str, val)


#@ ensures \result == val
def call_list(val) -> int:
    return Union(int, str, val)


#@ ensures \result == val
def call_none(val) -> int:
    return Union(int, str, val)


if __name__ == "__main__":
    assert call_string("not-an-int-or-str-arm") == "not-an-int-or-str-arm"
    assert call_list([1, 2, 3]) == [1, 2, 3]
    assert call_none(None) is None
    print("PASS")
