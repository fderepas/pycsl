r"""Test 7438 -- cv6 D4 (expected PASS): CONTROL -- a walrus in the FIRST operand of `and` read in the second and after the `if` (both dominated by the binding). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ ensures \result == x + 1
#@ assigns \nothing
def g(x: int) -> int:
    return x + 1


#@ ensures \result == x + 1
#@ assigns \nothing
def f(x: int) -> int:
    if (y := g(x)) > 0 and y < 100:
        return y
    return y
