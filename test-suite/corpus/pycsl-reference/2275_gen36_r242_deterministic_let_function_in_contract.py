r"""Test 2275 — route #242 (expected PASS): CONTROL. A DETERMINISTIC function with no writes stays a
`let function` and stays usable in a contract: `\result == sq(y) + 1` and `sq(y) == sq(y)` PROVE.
CPython `m(3)` = 10 = sq(3) + 1.
"""
# pycsl-expected: PASS


#@ assigns \nothing
def sq(x: int) -> int:
    return x * x


#@ ensures \result == sq(y) + 1
#@ assigns \nothing
def m(y: int) -> int:
    if sq(y) == sq(y):
        return sq(y) + 1
    return 0
