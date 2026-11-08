r"""Test 2799 — route #265 (expected FAIL, refused): `case True:` is an IDENTITY test (PEP 634),
and `1 is True` is False, so CPython returns 0. The pattern lowered to `(x = 1)` and
`\result == 1` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = 1
    match x:
        case True:
            return 1
        case _:
            return 0

if __name__ == "__main__":
    print(f())
