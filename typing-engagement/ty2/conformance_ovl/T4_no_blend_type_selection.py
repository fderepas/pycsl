"""Static gate T4 — the no-blend witness: selection by type ALONE, no runtime isinstance.

Spec clause O5 (§1.2): "The static overload-selection obligation (O4) is
discharged by a type-based VC — the argument's static type against the stub's
parameter type. It must NOT be discharged by the implementation's runtime
`isinstance` dispatch. A lowering that let `if isinstance(x, int): ...` in the
implementation SATISFY the static 'the int overload's postcondition applies'
obligation would blend the planes."

This driver is the load-bearing no-blend witness for the STATIC side: the
implementation has NO `isinstance` branch whatsoever — its body is an
unconditional `return x`. The int overload's guarded postcondition
`isinstance(x, int) -> \result == x` must still apply at the call site `f(5)`,
discharged by TYPE alone (the argument `5` has static type `int`), NOT by any
runtime isinstance dispatch in the body. If the selection were blended into the
runtime dispatch, an implementation with no isinstance branch could not
discharge the call-site postcondition.

Expected (from spec): prove — the int stub's guarded postcondition applies at
the call site by type-based selection alone, even though the implementation
body has NO isinstance branch.
"""

from typing import overload


#@ ensures \result == x
@overload
def f(x: int) -> int: ...


def f(x: int) -> int:
    return x  # NO isinstance branch — selection is purely type-based


#@ ensures \result == 5
def g() -> int:
    return f(5)


if __name__ == "__main__":
    assert g() == 5
    print("PASS")
