r"""Test 5035 -- gen #37 route #372 (expected FAIL): `m: Dict[int, D]`, `{m[0]}` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[int, D]) -> int:
    if 0 in m:
        s = {m[0]}
    return 1

if __name__ == "__main__":
    print(g({0: D(1)}))
