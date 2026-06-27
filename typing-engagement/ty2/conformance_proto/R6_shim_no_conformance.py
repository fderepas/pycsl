"""Runtime gate R6 — no static conformance at runtime: the shim cannot discharge
any refinement VC.

Spec clause R6 (§2.2): "The runtime does NOT perform the static conformance
check (P2). A value that fails static conformance but has all member attributes
PRESENT will PASS isinstance(x, P) at runtime. This is the runtime-side
restatement of the no-blend rule (P5)."

This driver confirms the runtime-side no-blend: the shim's identity
postcondition `ensures \result == val` is OPAQUE to the static plane — it
carries ONLY the identity, so it CANNOT discharge any contract-refinement VC.
A `val` that is provably outside any protocol's conformance (a bare int) still
passes the shim unchanged, because the shim performs no conformance check.

Expected (from spec): PASS — the shim's identity postcondition discharges for a
bare int value, regardless of conformance (R6: no static conformance at runtime).
"""

from pycsl_lib.typ import runtime_checkable


#@ ensures \result == val
def shim_no_conformance(val: int) -> int:
    return runtime_checkable(None, val)


if __name__ == "__main__":
    assert shim_no_conformance(42) == 42
    print("PASS")
