r"""Test 2792 — route #264 (expected FAIL, refused): `del x` unbinds `x`, so `return x` raises
`UnboundLocalError`. `del name` lowered to `()` and the read kept the old value: `\result == 1`
PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = 1
    del x
    return x

if __name__ == "__main__":
    try:
        print(f())
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
