r"""Test 4714 -- gen #37 route #350 (expected FAIL): a nested `def g(x: int = "a")` PROVED `x * 0 + 1` under `no_exception \all` (CPython TypeError). REFUSED now (route #350).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    def g(x: int = "a") -> int:  # type: ignore
        return x * 0 + 1
    return g()

if __name__ == "__main__":
    print(f())
