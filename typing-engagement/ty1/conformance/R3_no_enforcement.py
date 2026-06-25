"""Runtime gate R3 — no enforcement (identity holds for ANY value).

Spec clause R3 (union-twoplane-spec.md §2.1): the runtime does NOT check that a
value stored under a `Union[X, Y]` annotation is of type `X` or `Y`. The shim
must agree with S4: it constructs the introspectable object and performs NO
validation of annotated values — a shim that CHECKED arm membership would be
unfaithful (R8). The identity postcondition `#@ ensures \\result == val`
must discharge for ANY value (R3, R8).

This driver calls the `Union` shim directly with values that are NOT in any
arm of any declared Union — a string, a list, None — and expects the identity
postcondition to discharge regardless. (R8 forbids the shim from validating
arm membership.)

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
    assert call_string("not-an-int-or-int-arm") == "not-an-int-or-int-arm"
    assert call_list([1, 2, 3]) == [1, 2, 3]
    assert call_none(None) is None
    print("PASS")
