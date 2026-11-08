r"""Test 4860 -- gen #37 route #361 (expected FAIL): witness r23: `k: InitVar[int]` read as `d.k` under `no_exception \all` PROVED (CPython AttributeError). REFUSED (PYCSL-R361-DATACLASS-PSEUDO-FIELD, route #361).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar

@dataclass
class D:
    x: int
    k: InitVar[int]

#@ no_exception \all
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1, 2)))
