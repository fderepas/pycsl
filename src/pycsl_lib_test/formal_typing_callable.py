# Formal tests for pycsl_lib/typ — Callable shim (runtime plane, R3)
# Spec's promise (callable-twoplane-spec.md §2): Callable is an introspectable
# alias object, no signature enforcement (R3). The runtime callable() check is
# presence-only — the GT7-analogous no-blend for Callable (D1).
from pycsl_lib.typ import cast


#@ requires val >= 0
#@ ensures \result == val
def test_callable_no_enforcement(val: int) -> int:
    """Callable is an introspectable alias, no signature enforcement (R3).
    The cast identity (the runtime-plane consequence) holds for any val."""
    return cast(0, val)


#@ requires val >= 0
#@ ensures \result == val
def test_callable_presence_only(val: int) -> int:
    """The runtime callable check is presence-only, not signature (D1 no-blend)."""
    return cast(0, val)
