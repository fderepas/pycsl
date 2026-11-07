r"""Test 5008 -- gen #37 route #369 (expected FAIL): NEW latent: `D(1, 5)` against an explicit `__init__(self, x)` was never arity-checked (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
class D:
    def __init__(self, x: int) -> None:
        self.x = x

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
