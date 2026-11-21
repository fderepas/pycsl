r"""Test 4994 -- gen #37 route #369 (expected FAIL): `k: IV[int]` hides route #362's invariant refusal (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar as IV

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    k: IV[int]

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(-1, 0)))
