r"""Test 4715 -- gen #37 route #350 (expected FAIL): `K = 0.5; def f(x: int = K)` PROVED `\result == 0` (CPython 0.5): the bare-name default resolves to the module constant. REFUSED now (route #350).
"""
# pycsl-expected: FAIL
K = 0.5
#@ ensures \result == 0
def f(x: int = K) -> int:  # type: ignore
    return x % 1

if __name__ == "__main__":
    print(f())
