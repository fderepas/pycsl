"""Test 0055 — Python Reference 3.2.8.6: Built-in functions"""
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def test_built_in_functions() -> int:
    """Ref 3.2.8.6: `min` and `max` are built-in functions, and the contract SAYS what
    they return here rather than leaving it to an `assert` (which Module 6 DROPS).
    Previously the whole body was `\"\"\"Ref 3.2.8.6: Built-in functions.\"\"\"; return 0`
    (relaunch #46, `bin/check-vacuous-drivers.py`).

    TWO LIMITS MEASURED WHILE WRITING THIS, recorded so the next reader does not
    rediscover them:

    * `abs` IS SOUND BUT INCOMPLETE ON A NEGATIVE ARGUMENT. `abs(4) == 4` proves;
      `abs(-4) == 4` does NOT, and neither does `abs(-4) == -4`, `abs(-4) == 0`, nor
      `#@ requires x < 0; #@ ensures \\result == -x` on `return abs(x)`. So nothing
      FALSE about `abs` is provable — it is a completeness gap, not a route.
    * Conjoining `len(xs) == 3` on a list local with three arithmetic identities in one
      goal sends Alt-Ergo past 48 M steps and times out at 30 s. `len` is exercised by
      0056 instead, on its own goal. An SMT-scale limit of the conjoined goal, not a
      modelling gap."""
    if min(5, 2) == 2 and max(5, 2) == 5:
        return 1
    return 0

if __name__ == "__main__":
    assert test_built_in_functions() == 1
