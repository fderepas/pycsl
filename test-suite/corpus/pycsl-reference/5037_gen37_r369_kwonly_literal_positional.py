r"""Test 5037 -- gen #37 route #369 (expected FAIL): NEW latent: literal `_: KW_ONLY`, `D(1, 2)` passes the keyword-only `y` positionally (never arity-checked) (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, KW_ONLY

@dataclass
class D:
    x: int
    _: KW_ONLY
    y: int = 0

#@ no_exception \all
def f() -> int:
    d = D(1, 2)
    return d.x

if __name__ == "__main__":
    print(f())
