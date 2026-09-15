r"""Test 1359 — ROUTE #122 (carrier of the first battery-B draft): `other()` defines a helper `inc` (+1) BEFORE a module `def inc` (-1); the module def won the name, the helper never reached emission, and `other()` PROVED `\result == -1` while CPython returns 1. The collision is now checked from both sides.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == -1
#@ assigns \nothing
def other() -> int:
    def inc(y: int) -> int:
        return y + 1
    return inc(0)


#@ ensures \result == y - 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y - 1
