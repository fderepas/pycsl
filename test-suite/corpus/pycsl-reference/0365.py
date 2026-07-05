"""Test 0365 — ZeroDivisionError with a branching precondition.

The disjunctive precondition `n > 0 or n < 0` excludes zero. SMT
solvers handle this rephrasing well; the inline no_div_zero assert
discharges.
"""
_ = 0  # anchor
#@ requires n > 0 or n < 0
#@ ensures \result == 100 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def branching_div(n: int) -> int:
    return 100 // n


if __name__ == "__main__":
    assert branching_div(5) == 20
    assert branching_div(-5) == -20
