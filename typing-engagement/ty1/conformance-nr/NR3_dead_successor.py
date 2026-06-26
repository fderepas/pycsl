"""Static gate NR3 (negative) — a statement after a NoReturn call is dead code.

Spec clause NR3 (noreturn-twoplane-spec.md §1.1): a statement immediately
following a call to a `NoReturn`-annotated function is statically
UNREACHABLE — the callee's `false` postcondition (NR1) makes the
continuation path's path-condition contradictory. PyCSL reports this as
dead code (the dead-branch class — a dead branch proves `false` SOUNDLY,
which is NOT vacuity). The successor is a static warning/error, NOT a
VC-failure.

Here `f` is `-> NoReturn` and raises (NR1/NR2a satisfied). `caller` calls
`f()` then executes `x = 1; return x` — the `x = 1` is unreachable.

Expected (from spec): FAIL (PIPELINE ERROR) — the dead-successor check
(`_check_noreturn_successors`) flags the statement following the `f()` call
as unreachable at the semantic-analysis stage.
"""

from typing import NoReturn


def f() -> NoReturn:
    raise Exception()


#@ ensures \result == 1
#@ assigns \nothing
def caller() -> int:
    f()
    x = 1   # NR3: dead code — unreachable (f never returns normally)
    return x


if __name__ == "__main__":
    # Runtime: f() raises, so caller never reaches `x = 1`. The static gate
    # must FAIL because the successor is statically unreachable.
    try:
        caller()
    except Exception:
        print("PASS")
