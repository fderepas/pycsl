r"""Test 4173 -- gen #37 route #321 (expected PASS): CONTROL: `defaultdict(lambda: 0)` answers 0 like `int`: PROVES.
"""
# pycsl-expected: PASS
from typing import Dict
from collections import defaultdict
#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = defaultdict(lambda: 0)
    d[1] += 4
    return d[1]

if __name__ == "__main__":
    assert f() == 4, f()
