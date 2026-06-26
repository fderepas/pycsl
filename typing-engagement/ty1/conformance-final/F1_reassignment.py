"""Static gate F1- — reassigning a module-level Final name is a static error.

Spec clause F1 (final-twoplane-spec.md §1.1, S5 case (b)): a module-level
`Final` name may be written ONLY at its declaration. Any subsequent
assignment to `x` — including a reassignment inside a function body — is a
static error, raised by the syntactic write-site check (F1 arm of
`_check_final`, a degenerate HAPPY no-write confinement — NOT a VC).

The runtime would happily execute the reassignment (FR3 — the runtime
does NOT enforce the write-restriction); the rejection is a static-plane
judgment only (FD1 divergence, FD2 no-blend).

Expected (from spec): FAIL (PIPELINE ERROR) — the syntactic write-site
check raises `PyCSLSemanticError` at the semantic-analysis stage, before
any WhyML is emitted. If this driver PASSES, the static write-policy is
not being enforced (a blend or a missing check).
"""

from typing import Final

x: Final[int] = 5


#@ assigns \nothing
def f() -> int:
    x = 6
    return x


if __name__ == "__main__":
    # Runtime would execute the reassignment (FR3); static gate must FAIL.
    assert f() == 6
    print("PASS")
