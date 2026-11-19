r"""Test 2796 — route #264 (expected FAIL, refused): `y` is bound only inside the body of a
`for` over `range(n)`, which is EMPTY under `n <= 0`; CPython `f(0)` raises
`UnboundLocalError`. `\result == 0` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ requires n <= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    #@ loop invariant 0 <= k and y == 0
    #@ loop variant n - k
    for k in range(n):
        y = 1
    return y

if __name__ == "__main__":
    try:
        print(f(0))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
