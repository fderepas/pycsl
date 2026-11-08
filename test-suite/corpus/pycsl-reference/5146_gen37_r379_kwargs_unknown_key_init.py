r"""Test 5146 -- gen #37 route #379 (expected FAIL): `C(**{"y": 1})` against `__init__(self, x)` under `no_exception` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self, x: int) -> None:
        self.x = x

#@ no_exception \all
def f() -> int:
    kw = {"y": 1}
    c = C(**kw)
    return 1

if __name__ == "__main__":
    print(f())
