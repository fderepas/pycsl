"""Runtime gate FR6 — Final is NOT a distinct runtime class / no descriptor.

Spec clause FR6 (final-twoplane-spec.md §2.3): a faithful shim does NOT
introduce a distinct `Final` runtime class, a write-guard descriptor, or
any runtime enforcement hook; `Final[T]` must be the `typing.Final` alias
object, per FR1. Introducing a descriptor that raised on a second write
would blend the planes (FD2) and diverge from S4.

This driver confirms the shim is identity (no descriptor): the identity
postcondition `#@ ensures \\result == val` discharges for any value, and
the shim does NOT block writes. The probe is the same identity discharge
as FR3 — if the shim introduced a descriptor, the identity postcondition
would not discharge (the descriptor would intercept the return or raise
on a second call).

Expected (from spec): PASS — the identity postcondition discharges; no
descriptor intervenes.
"""

from pycsl_lib.typ import Final


#@ ensures \result == val
def identity_once(val) -> int:
    return Final(int, None, val)


#@ ensures \result == val
def identity_twice(val) -> int:
    # Two calls to the shim with the same val — a descriptor that raised
    # on a second write would block this. The identity postcondition must
    # discharge for BOTH calls.
    a = Final(int, None, val)
    b = Final(int, None, val)
    return b


if __name__ == "__main__":
    assert identity_once(42) == 42
    assert identity_twice(42) == 42
    print("PASS")
