r"""Test 5150 -- gen #37 route #379 (expected FAIL): `C(**kw).x == 0` through an explicit `__init__` (CPython 5). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result == 0
def f() -> int:
    kw = {"x": 5}
    c = C(**kw)
    return c.x

if __name__ == "__main__":
    print(f())
