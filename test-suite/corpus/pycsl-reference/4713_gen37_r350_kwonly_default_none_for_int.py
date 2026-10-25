r"""Test 4713 -- gen #37 route #350 (expected FAIL): a kw-only `*, x: int = None` PROVED `x * 0 + 1` under `no_exception \all` (CPython TypeError). REFUSED now (route #350).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 1
def f(*, x: int = None) -> int:  # type: ignore
    return x * 0 + 1

if __name__ == "__main__":
    print(f())
