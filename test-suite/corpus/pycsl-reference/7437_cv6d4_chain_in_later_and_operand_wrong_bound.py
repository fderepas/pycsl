r"""Test 7437 -- cv6 D4 (expected FAIL, verify-fail): NON-VACUITY twin of 7436 -- the same body with a wrong upper bound in the contract (`x + 1 <= 9`). Refused at base 4d15b89a7 (route #264); now emitted and the postcondition FAILS (x = 9: f returns 1, the claim says 0).
"""
# pycsl-expected: FAIL
#@ ensures \result == x + 1
#@ assigns \nothing
def g(x: int) -> int:
    return x + 1


#@ ensures \result == 1 <==> (c and 0 <= x + 1 and x + 1 <= 9)
#@ assigns \nothing
def f(c: bool, x: int) -> int:
    if c and 0 <= g(x) <= 10:
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(True, 9), "VIOLATION (claim says 0)")
