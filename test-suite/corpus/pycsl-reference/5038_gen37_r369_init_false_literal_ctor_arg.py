r"""Test 5038 -- gen #37 route #369 (expected FAIL): NEW latent: literal `field(init=False, default=4)`, `D(1, 2)` passes an argument for it (never arity-checked) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

@dataclass
class D:
    x: int
    y: int = field(init=False, default=4)

#@ no_exception \all
def f() -> int:
    d = D(1, 2)
    return d.x

if __name__ == "__main__":
    print(f())
