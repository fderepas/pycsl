"""NO-BLEND check (sharpened for Final) — the runtime shim must NOT rescue a static write-policy violation.

Spec clause FD2 (final-twoplane-spec.md §3, the load-bearing Final
no-blend divergence): the static plane's write-policy check (F1/F2) is a
proof-time / static-analysis judgment — it asks "is there a write site
outside the allowed perimeter?" — a syntactic property of the program,
discharged independently of any execution. The runtime plane's
no-enforcement (FR3) means a write at runtime succeeds. A lowering that
let the runtime success of a write SATISFY the static write-policy check
would blend the planes: the static VC is the write-policy check (does a
disallowed write site exist?), independent of runtime behaviour.

This is the NO-BLEND probe for FD2: a driver that REASSIGNS a Final name
(a static error per F1) but ALSO invokes the runtime `Final` shim. If
the lowering blends the planes — i.e. the runtime shim's identity
discharge "rescues" the static write-policy violation and the driver
PASSES — that is the blend. If the lowering is faithful, the static
write-policy check STILL fires (the reassignment is a disallowed write
site, regardless of whether the shim is invoked), and the driver FAILS
with a PIPELINE ERROR at the semantic-analysis stage.

Concretely: `x: Final[int] = 5` is the declaration write (module scope,
permitted). `g` reassigns `x` inside a function body (a disallowed
write site per F1) AND calls the `Final` shim. The static write-site
check must flag the reassignment in `g` — the shim invocation must NOT
rescue it.

Expected (from spec): FAIL (PIPELINE ERROR) — the syntactic write-site
check raises `PyCSLSemanticError` for the reassignment of `x` in `g`,
independently of the `Final` shim call. If this driver PASSES, the
runtime shim is blending the planes (FD2 violation): the static
write-policy is being discharged by the runtime shim's identity
postcondition instead of by the syntactic write-site check.
"""

from typing import Final
from pycsl_lib.typ import Final as FinalShim

x: Final[int] = 5


#@ ensures \result == 6
#@ assigns \nothing
def g(val) -> int:
    # Reassignment of a module-level Final name — a static error per F1.
    # The runtime shim is invoked below; it must NOT rescue this.
    x = 6  # static-plane write-site violation (F1)
    return FinalShim(int, None, val)


if __name__ == "__main__":
    # Runtime would execute the reassignment (FR3) and the shim (FR3);
    # the static gate must FAIL because of the F1 write-site violation.
    assert g(6) == 6
    print("PASS")
