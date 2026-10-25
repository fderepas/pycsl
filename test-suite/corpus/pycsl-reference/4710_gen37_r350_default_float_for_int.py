r"""Test 4710 -- gen #37 route #350 (expected FAIL): `def f(x: int = 0.5)` PROVED `\result == 0` for `x % 1` (CPython `f()` = 0.5). REFUSED now (PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH, route #350).
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
def f(x: int = 0.5) -> int:  # type: ignore
    return x % 1

if __name__ == "__main__":
    print(f())
