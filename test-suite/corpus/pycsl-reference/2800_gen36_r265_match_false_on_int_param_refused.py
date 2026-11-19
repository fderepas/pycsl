r"""Test 2800 — route #265 (expected FAIL, refused): `case False:` on `n: int`; `0 is False` is
False, so CPython `f(0)` returns 0, not 7. `n == 0 ==> \result == 7` PROVED at 283d1033.
"""
# pycsl-expected: FAIL
#@ ensures n == 0 ==> \result == 7
#@ assigns \nothing
def f(n: int) -> int:
    match n:
        case False:
            return 7
        case _:
            return 0

if __name__ == "__main__":
    print(f(0))
