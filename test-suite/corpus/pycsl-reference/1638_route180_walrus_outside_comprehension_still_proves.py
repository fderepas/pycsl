r"""Test 1638 - ROUTE #180 control (gen #29): a walrus in an ordinary condition (not inside a comprehension) is still modelled: `(y := x * 2) > 10` with x = 6 returns 12.
"""
_ = 0  # anchor


#@ ensures \result == 12
def probe() -> int:
    x = 6
    if (y := x * 2) > 10:
        return y
    return 0
