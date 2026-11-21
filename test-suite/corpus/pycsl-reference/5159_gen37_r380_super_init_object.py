r"""Test 5159 -- gen #37 route #380 (expected FAIL): NEW latent: `super().__init__(5)` in a class over `object` under `no_exception` (CPython TypeError: `object.__init__` takes exactly one argument; PROVED at base b815ee8d8).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        super().__init__(5)
        self.x = 1

#@ no_exception \all
def f() -> int:
    c = C()
    return 1

if __name__ == "__main__":
    print(f())
