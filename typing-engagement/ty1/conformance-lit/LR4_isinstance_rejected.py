"""Runtime gate LR4 — `isinstance` against `Literal` is NOT supported.

Spec clause LR4 (literal-twoplane-spec.md §2.2): `isinstance(v, Literal[1, 2])`
raises `TypeError` at runtime — `typing.Literal` aliases are not valid
second arguments to `isinstance`. The runtime has no membership test for
the literal value set.

Per LR8 (§2.4), a faithful shim does NOT introduce a distinct `Literal`
runtime class — `Literal[v1, ..., vn]` must be the `typing.Literal` alias
object, not a runtime type that `isinstance` could check against.

This driver probes whether the lowering treats `isinstance(v, Literal[...])`
as a narrowing guard (it must NOT, per LR4/LR8): the True branch returns 0,
the False branch returns 1, and the postcondition
`ensures \\result == 0 \\/ \\result == 1` would discharge trivially for ANY
boolean-valued condition. The sharpened claim is that the True branch
NARROWS the value of `v` to a concrete `Literal` value (it must NOT — the
shim has no membership test). So the postcondition on the True branch is
sharpened to `ensures \\result == 0`, which depends on the
`isinstance(...)` returning True for `v = 0` and the body returning 0.
Since `isinstance` against the Literal shim is NOT a real runtime check
(LR4), PyCSL must not be able to prove the narrowed postcondition
`\\result == 0` from `isinstance(v, Literal[1, 2])` — it would have to
either reject the construct (faithful) or treat it as an opaque
uninterpreted boolean (which cannot narrow `v`'s value).

Expected (from spec): FAIL — `isinstance(v, Literal[1, 2])` is not
supported by the runtime shim; the narrowed postcondition cannot be
discharged from the uninterpreted boolean.
"""

from typing import Literal


#@ ensures \result == 0
#@ assigns \nothing
def f(v) -> int:
    if isinstance(v, Literal[1, 2]):
        return 0
    return 1


if __name__ == "__main__":
    print("PASS")
