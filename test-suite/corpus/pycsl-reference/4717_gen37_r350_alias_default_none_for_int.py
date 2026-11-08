r"""Test 4717 -- gen #37 route #350 (expected FAIL): `Num = int; def f(x: Num = None)` PROVED under `no_exception \all` (CPython TypeError): module aliases are followed. REFUSED now (route #350).
"""
# pycsl-expected: FAIL
Num = int
#@ no_exception \all
#@ ensures \result == 1
def f(x: Num = None) -> int:  # type: ignore
    return x * 0 + 1

if __name__ == "__main__":
    print(f())
