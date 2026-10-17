r"""Test 2795 — route #264 (expected FAIL, refused): `y` is bound only by the `case 1:` arm and
the `match` has no catch-all, so `f(2)` falls through and `return y` raises
`UnboundLocalError`. `\result == 0` (the hoisted default) PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ requires x == 2
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    match x:
        case 1:
            y = 1
    return y

if __name__ == "__main__":
    try:
        print(f(2))
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
