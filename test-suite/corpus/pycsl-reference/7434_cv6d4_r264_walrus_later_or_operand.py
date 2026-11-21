r"""Test 7434 -- cv6 D4 (expected FAIL, refused, route #264): a walrus in the SECOND operand of `or` read after the `or`. The short-circuit is now modelled as control flow (operand k runs after operands 0..k-1); the JOIN keeps only the first operand's bindings, so `y` is still not definitely assigned. CPython f(True): UnboundLocalError.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f(c: bool) -> int:
    if c or (y := 1) > 5:
        pass
    return y


if __name__ == "__main__":
    try:
        print("result", f(True))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
