r"""Test 2798 — route #264 CONTROL (expected PASS): the loop is over the constant NON-EMPTY
`range(3)`, so its first iteration is certain and `y`, bound in the body, is definitely
assigned after it. CPython returns 5.
"""
# pycsl-expected: PASS
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    #@ loop invariant 0 <= k and k <= 3
    #@ loop invariant k > 0 ==> y == 5
    #@ loop variant 3 - k
    for k in range(3):
        y = 5
    return y

if __name__ == "__main__":
    print(f())
