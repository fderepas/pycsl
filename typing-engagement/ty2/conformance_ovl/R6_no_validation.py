"""Runtime gate R6/R7 — no validation in the shim; the implementation is a plain function.

Spec clause R6 (§2.3): "Any `src/pycsl_lib/typing` shim for `overload` must
agree with S4: the decorator registers the stub and returns a dummy; it performs
NO type-checking of arguments."

Spec clause R7 (§2.3): "The runtime plane of the implementation is just the
plain-function plane — there is no separate overload runtime behaviour beyond
the registry and the dummy."

This driver: invoke the `overload` shim with an `int` value (provably not a
function object). The shim models the decorator returning a dummy and performs
NO validation — the identity postcondition discharges for any value, confirming
the shim carries only the identity contract (no overload-resolution check).

Expected (from spec): prove identity (the shim performs no validation).
"""

from pycsl_lib.typ import overload


#@ ensures \result == val
def f(val) -> int:
    return overload(None, val)


if __name__ == "__main__":
    # an int value is provably not a function object; if the shim validated
    # its argument this postcondition would not discharge.
    assert f(42) == 42
    print("PASS")
