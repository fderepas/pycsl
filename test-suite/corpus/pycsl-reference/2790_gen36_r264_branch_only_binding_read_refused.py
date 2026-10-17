r"""Test 2790 — route #264 (expected FAIL, refused): `y` is bound only on the True branch and
read after the `if`. CPython `f(False)` raises `UnboundLocalError`; the read used to be the
hoisted default `ref 0`, so `\result >= 0` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ ensures \result >= 0
#@ assigns \nothing
def f(c: bool) -> int:
    if c:
        y = 1
    return y

if __name__ == "__main__":
    try:
        print(f(False))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
