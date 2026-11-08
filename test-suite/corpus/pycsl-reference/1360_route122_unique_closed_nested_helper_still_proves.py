r"""Test 1360 — ROUTE #122/#126 positive control: a nested helper with a UNIQUE name that reads nothing from its enclosing function is lifted faithfully, and the true `\result == 4` still PROVES.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    def helper_unique_1360(y: int) -> int:
        return y + 1
    return helper_unique_1360(3)
