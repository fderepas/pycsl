r"""Test 1537 - ROUTE #158 control (gen #29): `all(x > 0 for x in [1, 2])` keeps the faithful fold and `\result == 1` PROVES on both sides of the repair.
"""
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    return 1 if all(x > 0 for x in [1, 2]) else 0

