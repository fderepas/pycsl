r"""Test 2791 — route #264 (expected FAIL, refused): `n += 1` on a name bound nowhere else.
`n` is local (the augmented assignment binds it), so the read raises `UnboundLocalError`;
it used to read the default 0 and `\result == 1` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n += 1
    return n

if __name__ == "__main__":
    try:
        print(f())
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
