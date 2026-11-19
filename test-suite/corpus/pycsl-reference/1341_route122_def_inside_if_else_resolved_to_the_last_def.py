r"""Test 1341 — ROUTE #122: two defs of `inc` in the arms of a module-level `if`; the model kept the textually LAST (the else arm, +1) and PROVED `inc(3) == 4` while CPython takes the if arm and returns 2. A module-scope def inside a compound statement that competes with another binding is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
FLAG = 1
if FLAG == 1:
    #@ ensures \result == y - 1
    #@ assigns \nothing
    def inc(y: int) -> int:
        return y - 1
else:
    #@ ensures \result == y + 1
    #@ assigns \nothing
    def inc(y: int) -> int:
        return y + 1


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
