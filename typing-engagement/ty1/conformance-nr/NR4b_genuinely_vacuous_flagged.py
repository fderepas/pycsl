"""Static gate NR4 — half B — a genuinely-vacuous function (NO NoReturn) is STILL flagged.

Spec clause NR4 (noreturn-twoplane-spec.md §1.2 — THE LOAD-BEARING CLAUSE,
soundness half B): the vacuity-gate exemption is keyed on the `-> NoReturn`
ANNOTATION, NOT on the inferred `false` postcondition. The latter would
exempt EVERY genuinely-vacuous function, defeating the gate. So a function
with an inconsistent context (here: contradictory preconditions
`requires x > 0` AND `requires x < 0`) that has NO `NoReturn` annotation
must STILL be probed and flagged.

This is the soundness check: the exemption is keyed on the annotation, not
on the inferred postcondition. If half B FAILS (the genuinely-vacuous
function is NOT flagged), the exemption is over-broad and the gate is
unsound — it would silently accept meaningless greens.

Run with: pycsl NR4b_genuinely_vacuous_flagged.py --check-vacuity

Expected (from spec): FAIL (VACUITY GATE FAILED) — the contradictory
preconditions make the context inconsistent, so the injected `false`-goal
proves Valid and `g` is flagged as vacuously green. The NoReturn exemption
does NOT extend to it (it has no `-> NoReturn` annotation).
"""


#@ requires x > 0
#@ requires x < 0
#@ ensures \result == x
#@ assigns \nothing
def g(x: int) -> int:
    return x


if __name__ == "__main__":
    # Runtime: g(5) would return 5 (NR-R3 — no enforcement of preconditions
    # at runtime); the static vacuity gate must FAIL because the context is
    # inconsistent.
    print(g(5))  # noqa: runtime-only; never reached under pycsl --check-vacuity
