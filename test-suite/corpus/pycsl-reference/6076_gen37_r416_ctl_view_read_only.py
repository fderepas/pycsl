r"""Test 6076 -- gen #37 route #416 (expected PASS): CONTROL: iterating `d.keys()` / `d.values()` / `d.items()` while mutating a DIFFERENT dict `e`, under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict


#@ no_exception \all
def f(d: Dict[int, int], e: Dict[int, int]) -> int:
    for k in d.keys():
        e[k + 100] = 0
    for v in d.values():
        e[v + 100] = 0
    for k2, v2 in d.items():
        e[k2 + 100] = v2
    return 0


if __name__ == "__main__":
    print(f({1: 1}, {}))
