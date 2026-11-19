r"""Test 5031 -- gen #37 route #372 (expected FAIL): `xs: List[D]`, `{xs[0]}` (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    xs: List[D] = [d]
    s = {xs[0]}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
