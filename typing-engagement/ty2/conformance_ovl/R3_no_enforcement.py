"""Runtime gate R3 — no enforcement (identity holds for ANY value).

Spec clause R3 (overload-twoplane-spec.md §2.1): "The runtime does NOT check
that the argument's type matches any overload stub's parameter type. The
implementation accepts whatever runtime arguments it accepts; wrong-typed
arguments flow through unless the implementation's own code rejects them — and
that is the implementation's logic, NOT overload enforcement."

Spec clause R6 (§2.3): "Any `src/pycsl_lib/typing` shim for `overload` must
agree with S4: the decorator registers the stub and returns a dummy; it performs
NO type-checking of arguments. A shim that CHECKED whether a call matches an
overload's parameter types would be unfaithful."

This driver: call the `overload` shim with a `val` that is a list (provably
outside any overload's parameter type). The shim's identity postcondition
`ensures \result == val` must discharge regardless of the value's type — the
shim performs NO type enforcement.

Expected (from spec): prove identity (no type check fires).
"""

from pycsl_lib.typ import overload


#@ ensures \result == val
def f(func, val) -> int:
    return overload(func, val)


if __name__ == "__main__":
    # a list value is NOT an int/str parameter type; if the shim validated the
    # value's type this postcondition would not discharge.
    assert f(lambda: None, [1, 2, 3]) == [1, 2, 3]
    print("PASS")
