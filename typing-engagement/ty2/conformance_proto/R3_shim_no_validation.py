"""Runtime gate R3/R4 — @runtime_checkable shim performs NO validation (identity).

Spec clause R3 (§2.1): "For a @runtime_checkable protocol P, isinstance(x, P)
returns True iff ... hasattr(x, m) is True. It checks attribute PRESENCE ONLY —
it does NOT check the member's signature, contract, or attribute types."
Spec clause R4 (§2.2): "Any src/pycsl_lib/typing shim for runtime_checkable must
agree with S4: it returns the class unchanged and performs NO signature check, NO
contract check, NO attribute-type check."

This driver exercises the runtime shim: `runtime_checkable(cls, val)` is called
with an arbitrary `val` (provably not a class object); the shim's identity
postcondition `ensures \result == val` must discharge regardless. The shim
performs NO validation (R4) — a shim that CHECKED conformance would be
unfaithful.

Expected (from spec): PASS — the shim's identity postcondition discharges for
any value (R3/R4: no enforcement, no validation).
"""

from pycsl_lib.typ import runtime_checkable


#@ ensures \result == val
def shim_is_identity(val: int) -> int:
    return runtime_checkable(None, val)


if __name__ == "__main__":
    assert shim_is_identity(7) == 7
    print("PASS")
