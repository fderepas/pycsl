r"""Test 2802 — route #265 (expected FAIL, refused): an OR-pattern `case 5 | True:` on `x = 1`;
`1` is neither 5 nor (identically) True, so CPython returns 0.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    x = 1
    match x:
        case 5 | True:
            return 1
        case _:
            return 0

if __name__ == "__main__":
    print(f())
