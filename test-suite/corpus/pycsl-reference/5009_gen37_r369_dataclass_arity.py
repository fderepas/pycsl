r"""Test 5009 -- gen #37 route #369 (expected FAIL): NEW latent: `D(1, 5)` against a one-field `@dataclass` was never arity-checked (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
