"""Test 0752 — non-vacuity gate self-test (default-on, fail-closed).

The non-vacuity gate is ON BY DEFAULT (non-lin-int-div-fixed.md T1): after a
file verifies, every body-bearing function is probed with an injected
`ensures false`. A function whose ASSUMED CONTEXT is logically inconsistent
proves that `false` on every normal-exit path, so its "green" is vacuous —
every postcondition (including a genuinely false one) discharges for free.
The gate FAILS such a run instead of reporting the meaningless success.

Here the two preconditions `a > b` and `b > a` are jointly unsatisfiable, so
`f`'s context is inconsistent and the (false) postcondition `\result == 0`
proves vacuously. Under the default gate this run is REJECTED — it is the
regression lock proving the silent false-green can no longer sail through.
Opt out only with `--no-check-vacuity`.
"""
_ = 0  # anchor
# pycsl-expected: FAIL
#@ requires a > b
#@ requires b > a
#@ ensures \result == 0
def f(a: int, b: int) -> int:
    """Inconsistent context (a > b AND b > a) → vacuous green → gate FAILs."""
    return a


if __name__ == "__main__":
    print("PASS")
