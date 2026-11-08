r"""Test 5155 -- gen #37 route #380 (expected FAIL): `super().__init__(y=1)` against `B.__init__(self, x)` (CPython TypeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
class B:
    def __init__(self, x: int) -> None:
        self.x = x

class C(B):
    def __init__(self) -> None:
        super().__init__(y=1)

#@ no_exception \all
def f() -> int:
    c = C()
    return 1

if __name__ == "__main__":
    print(f())
