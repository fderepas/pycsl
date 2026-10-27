r"""Test 6336 -- route #427 (expected PASS): CONTROL: a mutating loop over a SNAPSHOT (`list(d.keys())`) and a generator over ANOTHER dict, under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict


#@ no_exception \all
def f(d: Dict[int, int], e: Dict[int, int]) -> int:
    for k in list(d.keys()):
        d[k + 100] = 0
    for k in (x for x in e):
        d[k + 300] = 0
    return 0


if __name__ == "__main__":
    print(f({1: 1}, {2: 2}))
