"""Runtime gate R7 — no validation in the shim.

Spec clause R7 (typeddict-twoplane-spec.md §2.3): any `src/pycsl_lib/typing`
shim for `TypedDict` must agree with S4: it exposes the introspectable class
object and performs NO validation of annotated values. A shim that CHECKED
whether a value has the declared keys/types would be unfaithful in exactly the
way an over-strong axiom is. This driver calls the shim with a value
provably outside the TypedDict's key set (an int, not a dict); the identity
postcondition must discharge.

Expected (from spec): prove identity (no validation check fires).
"""

from pycsl_lib.typ import TypedDict


#@ ensures \result == val
def f(val) -> int:
    return TypedDict("Point", {"x": int, "y": int}, val)


if __name__ == "__main__":
    # an int value is NOT a dict; if the shim validated the value's shape this
    # postcondition would not discharge.
    assert f(42) == 42
    print("PASS")
