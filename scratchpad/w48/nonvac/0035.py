"""Test 0035 — Python Reference 2.6.2: Floating-point literals"""
_ = 0  # anchor
#@ requires 1.49 < x < 1.51
#@ ensures \result == 0
#@ assigns \nothing
def test_floating_point_literals(x: float) -> int:
    """Ref 2.6.2: a floating-point literal denotes a REAL value, and the notation is not
    the value — `1.49`, `1.490` and `149e-2` all denote the same number, as do `1.51` and
    `151e-2`. The guard below brackets `x` using the OTHER notation for each bound than the
    precondition uses, so it can only be discharged if all of them normalize to one real.
    Previously the whole body was `return 0` and the postcondition was discharged by the
    tail `return` alone (relaunch #46, `bin/check-vacuous-drivers.py`).

    TWO MEASURED LIMITS shape this driver, and both fail CLOSED:
      * float EQUALITY in a program guard is not modelled — `x == 1.5` emits `x = 1.5`
        typed as an int comparison and Why3 rejects it with "this expression has type real,
        but is expected to have type int". Only the ORDERINGS (`>.` `<.`) lower. So the
        driver brackets rather than equates.
      * a float LOCAL is worse than a float PARAM: `x: float = 1.5; y: float = 1.50;
        x == y` does not type-check either, which is the blocker relaunch #46 recorded
        against this very file. A float PARAMETER with a `requires` is the shape that
        works today.

    The precondition also exercises the CHAINED COMPARISON in a clause, which relaunch #48
    made mean the conjunction it reads as (§T.5.12j) — before that it was
    `((1.49 < x) < 1.51)` and type-rejected."""
    if x > 1.490 and x < 1.40:
        return 0
    return 1

if __name__ == "__main__":
    assert test_floating_point_literals(1.5) == 0
