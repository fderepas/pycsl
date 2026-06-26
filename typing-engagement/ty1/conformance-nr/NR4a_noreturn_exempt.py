"""Static gate NR4 — half A — a declared-NoReturn function is EXEMPTED from the vacuity probe.

Spec clause NR4 (noreturn-twoplane-spec.md §1.2 — THE LOAD-BEARING CLAUSE):
a function declared `-> NoReturn` carries the postcondition `false` BY
DESIGN (NR1). The non-vacuity gate (`--check-vacuity`) detects a vacuous
context by INJECTING `ensures { [@expl:vacprobe] false }` and flagging a
function whose injected `false`-goal proves Valid. A faithful `NoReturn`
function ALREADY HAS a `false` postcondition; it is INDISTINGUISHABLE from
a vacuous one under the probe and would be FALSE-POSITIVELY FLAGGED. The
gate MUST EXEMPT declared-`NoReturn` functions, KEYED ON THE `-> NoReturn`
ANNOTATION (the IR `is_noreturn` flag), NOT on the inferred postcondition.

This is half A of the soundness keystone: the NoReturn witness PASSES
`--check-vacuity` (exempted). Half B (NR4b) confirms a genuinely-vacuous
function is STILL flagged.

Run with: pycsl NR4a_noreturn_exempt.py --check-vacuity

Expected (from spec): PASS — the file verifies AND the non-vacuity gate
does NOT flag `f` (it is exempted via the `is_noreturn` IR flag).
"""

from typing import NoReturn


def f() -> NoReturn:
    raise Exception()


if __name__ == "__main__":
    try:
        f()
    except Exception:
        print("PASS")
