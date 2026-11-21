r"""Test 4175 -- gen #37 route #321 (expected FAIL): a `defaultdict` DEFAULT ARGUMENT is lowered at the call site, outside any scanned body; `f(5)` reads `d[5]` (inserting it) then tests `5 in d` (CPython 1). REFUSED: a defaultdict is modelled only in a scanned local assignment.
"""
# pycsl-expected: FAIL
from collections import defaultdict
from typing import Dict
#@ assigns \nothing
def f(k: int, d: Dict[int, int] = defaultdict(lambda: 0)) -> int:
    x = d[k]
    if k in d:
        return 1
    return 0

#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    return f(5)

if __name__ == "__main__":
    assert g() == 0, g()
