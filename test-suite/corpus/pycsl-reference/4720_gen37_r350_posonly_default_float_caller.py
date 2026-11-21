r"""Test 4720 -- gen #37 route #350 (expected FAIL): a positional-only `x: int = 0.5` called with the argument omitted (CPython 0.5). VERIFY-FAIL at base, REFUSED now (route #350).
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
def f(x: int = 0.5, /) -> int:  # type: ignore
    return x % 1

#@ ensures \result == 0
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g())
