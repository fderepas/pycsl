"""Runtime gate R8 — no validation in the shim.

Spec clause R8 (namedtuple-twoplane-spec.md §2.3): any `src/pycsl_lib/typing`
shim for `NamedTuple` must agree with S4: it exposes the introspectable class
object and performs NO validation of annotated values. A shim that CHECKED
whether a value has the declared field types would be unfaithful in exactly
the way an over-strong axiom is.

Expected (from spec): prove identity (no validation fires).
"""

from pycsl_lib.typ import NamedTuple


#@ ensures \result == val
def f(val) -> int:
    return NamedTuple("Point", [("x", int), ("y", int)], val)


if __name__ == "__main__":
    # an int value is provably not a tuple; if the shim validated the value's
    # shape this postcondition would not discharge.
    assert f(42) == 42
    print("PASS")
