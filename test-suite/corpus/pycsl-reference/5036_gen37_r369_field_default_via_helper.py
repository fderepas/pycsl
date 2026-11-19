r"""Test 5036 -- gen #37 route #369 (expected FAIL): NEW latent: `x: int = mk()` with `mk` returning `field(default=7)` read as an opaque default (`D().x == 0`) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

def mk() -> int:
    return field(default=7)

@dataclass
class D:
    x: int = mk()

#@ ensures \result == 0
def f() -> int:
    d = D()
    return d.x

if __name__ == "__main__":
    print(f())
