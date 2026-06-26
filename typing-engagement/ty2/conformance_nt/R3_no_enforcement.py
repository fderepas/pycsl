"""Runtime gate R3 — no enforcement (identity holds for ANY value).

Spec clause R3 (namedtuple-twoplane-spec.md §2.1): the runtime does NOT check
that a value stored under a `Point` annotation has fields `x`, `y` of types
`int`, `int`. The `NamedTuple` functional-form shim constructs the
introspectable class object and performs NO validation; the identity
postcondition must discharge for any `val`.

Expected (from spec): prove identity (no key/type check fires).
"""

from pycsl_lib.typ import NamedTuple


#@ ensures \result == val
def f(val) -> int:
    return NamedTuple("Point", [("x", int), ("y", int)], val)


if __name__ == "__main__":
    # a list value is NOT a tuple with fields x, y; if the shim validated the
    # fields this postcondition would not discharge.
    assert f([1, 2, 3]) == [1, 2, 3]
    print("PASS")
