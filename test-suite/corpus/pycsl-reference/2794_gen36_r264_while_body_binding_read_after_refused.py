r"""Test 2794 — route #264 (expected FAIL, refused): `y` is bound only inside a `while` body
that runs zero times under `n <= 0`, so CPython `f(0)` raises `UnboundLocalError`. The read
was the hoisted default 0 and `\result == 0` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ requires n <= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    k = n
    #@ loop invariant k == n and y == 0
    #@ loop variant k
    while k > 0:
        y = 1
        k = k - 1
    return y

if __name__ == "__main__":
    try:
        print(f(0))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
