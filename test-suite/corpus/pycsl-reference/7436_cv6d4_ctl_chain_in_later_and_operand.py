r"""Test 7436 -- cv6 D4 (expected PASS): CONTROL -- a chained comparison with a non-repeatable middle operand in the SECOND operand of `and`: `c and 0 <= g(x) <= 10` desugars to `c and (0 <= (_pycsl_cmp_1 := g(x)) and _pycsl_cmp_1 <= 10)`. REFUSED at base 4d15b89a7 (route #264: `_pycsl_cmp_1` not definitely assigned -- the walrus sat in a conditional operand); the read is dominated by the walrus, now PROVED.
"""
# pycsl-expected: PASS
#@ ensures \result == x + 1
#@ assigns \nothing
def g(x: int) -> int:
    return x + 1


#@ ensures \result == 1 <==> (c and 0 <= x + 1 and x + 1 <= 10)
#@ assigns \nothing
def f(c: bool, x: int) -> int:
    if c and 0 <= g(x) <= 10:
        return 1
    return 0
