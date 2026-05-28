"""Test 0344 — PyCSL Annotation Reference §3.1.18: Boolean atom in compound expressions.

Exercises `True` / `False` combined with `and`, `or`, and implication
(`==>`). A postcondition of `\\result >= 0 or False` is logically
equivalent to `\\result >= 0` — both directly discharged by SMT.

The test does not have a worked semantic content beyond demonstrating
that boolean atoms compose normally in `requires` / `ensures` clauses.
"""
#@ requires True and True
#@ ensures \result >= 0
#@ ensures \result >= 0 or False
#@ ensures True ==> \result >= 0
#@ ensures False ==> \result < 0
#@ assigns \nothing
def abs_int(x: int) -> int:
    if x >= 0:
        return x
    else:
        return -x

if __name__ == "__main__":
    assert abs_int(5) == 5
    assert abs_int(-5) == 5
    assert abs_int(0) == 0
    print("PASS")
