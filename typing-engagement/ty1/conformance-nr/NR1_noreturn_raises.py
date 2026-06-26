"""Static gate NR1 — `-> NoReturn` lowers to `ensures { false }`.

Spec clause NR1 (noreturn-twoplane-spec.md §1.0): a function annotated
`-> NoReturn` carries the postcondition `false` — it never returns normally
(it raises or diverges). The body `raise Exception()` has NO normal-exit
path, so the `false` postcondition is discharged by the ABSENCE of a
normal-exit path (not by an inconsistent context). This is the load-bearing
static clause: the same `ensures { false }` goal shape the non-vacuity gate
INJECTS (see NR4).

Expected (from spec): PASS — the false postcondition VC discharges because
the body raises (NR2a body-supports-divergence is satisfied); no normal
exit exists, so `false` holds vacuously-on-the-path, not vacuously-on-the-
context.
"""

from typing import NoReturn


def f() -> NoReturn:
    raise Exception()


if __name__ == "__main__":
    try:
        f()
    except Exception:
        print("PASS")
