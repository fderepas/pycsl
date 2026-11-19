r"""Test 2801 — route #265 (expected FAIL, refused): a GUARDED singleton arm
`case False if n == 0:` on `n = 0`; `0 is False` is False, so CPython returns 0.
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    n = 0
    match n:
        case False if n == 0:
            return 7
        case _:
            return 0

if __name__ == "__main__":
    print(f())
