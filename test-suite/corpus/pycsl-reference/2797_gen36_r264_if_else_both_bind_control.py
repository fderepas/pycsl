r"""Test 2797 — route #264 CONTROL (expected PASS): `y` is bound on EVERY branch of an
`if`/`elif`/`else`, so the read is definitely assigned. CPython `f(1), f(-1), f(0)` = 1, 2, 3.
"""
# pycsl-expected: PASS
#@ ensures \result >= 1 and \result <= 3
#@ assigns \nothing
def f(n: int) -> int:
    if n > 0:
        y = 1
    elif n < 0:
        y = 2
    else:
        y = 3
    return y

if __name__ == "__main__":
    print(f(1), f(-1), f(0))
