r"""Test 4711 -- gen #37 route #350 (expected FAIL): `def f(s: str = None)` PROVED `len(s)` under `no_exception \all` (CPython TypeError). REFUSED now (route #350).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result >= 0
def f(s: str = None) -> int:  # type: ignore
    return len(s)

if __name__ == "__main__":
    print(f())
