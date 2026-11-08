r"""Test 5158 -- gen #37 route #380 (expected FAIL): NEW latent: `super().__init__(5)` against `B.__init__(self)` under `no_exception` was never arity-checked (CPython TypeError; PROVED at base b815ee8d8).
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.x = 1

class C(B):
    def __init__(self) -> None:
        super().__init__(5)

#@ no_exception \all
def f() -> int:
    c = C()
    return 1

if __name__ == "__main__":
    print(f())
