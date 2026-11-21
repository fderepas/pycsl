"""v56 DISAGREE — ROUTE #90, SECOND OPERATOR. `is not True` lied the same way.

`1 is not True` is True in CPython, so this returns 1 while the model proved 0. Kept as a
separate driver because a repair scoped to `is True` alone would have left this proving.
"""


#@ requires x == 1
#@ ensures \result == 0
#@ assigns \nothing
def f(x: bool) -> int:
    if x is not True:
        return 1
    return 0


if __name__ == "__main__":
    print(f(1))
