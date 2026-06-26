"""NO-BLEND check (sharpened for NoReturn — NR-D2) — the runtime shim must NOT rescue a static false-postcondition violation.

Spec clause NR-D2 (noreturn-twoplane-spec.md §3 — the no-blend rule): the
static plane's `false` postcondition (NR1) MUST NOT be discharged by the
runtime's behaviour. Concretely: a `NoReturn`-annotated function that, at
runtime, is observed to raise does NOT thereby satisfy the NR1 obligation —
the static proof requires a proof-time argument (NR2a, a diverges-
supporting body) that EVERY normal-exit path is absent. Conversely, a
`NoReturn` function that the static plane proves divergent may, at runtime,
terminate without that being a static-plane failure. The runtime must not
be allowed to "pass" the static false-postcondition.

This is the NO-BLEND probe for NR-D2: a driver that declares a
`-> NoReturn` function whose body RETURNS (a static error per NR2a — the
false postcondition is violated) AND imports the runtime `NoReturn` shim.
If the lowering blends the planes — i.e. the runtime shim's alias-object
behaviour "rescues" the static NR2a violation and the driver PASSES — that
is the blend. If the lowering is faithful, the static body-supports-
divergence check STILL fires (the `return` is a normal-exit path,
regardless of whether the shim is imported), and the driver FAILS with a
PIPELINE ERROR at the semantic-analysis stage.

Concretely: `f` is `-> NoReturn` but its body is `return 1` (a static
error per NR2a). The `NoReturn` shim is imported (and the alias object is
referenced). The static body-supports-divergence check must flag the
`return` in `f` — the shim import must NOT rescue it.

Expected (from spec): FAIL (PIPELINE ERROR) — the body-supports-divergence
check raises `PyCSLSemanticError` for the `return` in `f`, independently of
the `NoReturn` shim import. If this driver PASSES, the runtime shim is
blending the planes (NR-D2 violation): the static false-postcondition is
being discharged by the runtime shim's alias-object behaviour instead of
by the body-divergence check.
"""

from typing import NoReturn
from pycsl_lib.typ import NoReturn as NoReturnShim   # runtime alias object


def f() -> NoReturn:
    return 1   # static-plane NR2a violation: body returns (normal-exit path)


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    _ = NoReturnShim   # touch the runtime shim — must NOT rescue the NR2a violation
    return f()


if __name__ == "__main__":
    # Runtime: g() would return 1 (NR-R3 — no enforcement); the static gate
    # must FAIL because of the NR2a body-does-not-diverge violation in f.
    print(g())  # noqa: runtime-only; never reached under pycsl
