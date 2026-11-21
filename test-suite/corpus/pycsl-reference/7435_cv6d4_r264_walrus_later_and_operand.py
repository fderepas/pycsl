r"""Test 7435 -- cv6 D4 (expected FAIL, refused, route #264): a walrus in the SECOND operand of `and` read after the statement. Not definite after the join. CPython f(False): UnboundLocalError.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f(c: bool) -> int:
    x = c and (y := 1) > 0
    return y


if __name__ == "__main__":
    try:
        print("result", f(False))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
