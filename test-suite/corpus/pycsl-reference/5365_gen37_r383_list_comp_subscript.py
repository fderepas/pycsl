r"""Test 5365 -- gen #37 route #383 (expected FAIL): `xs = [d for ..]; {xs[0]}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    xs = [d for _ in range(1)]
    s = {xs[0]}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
