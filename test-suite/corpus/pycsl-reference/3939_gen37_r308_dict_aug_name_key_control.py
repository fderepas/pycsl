r"""Test 3939 -- gen #37 route #308 (expected PASS): CONTROL: `d[k] += 2` with a name key keeps today's lowering and proves.
"""
# pycsl-expected: PASS
from typing import Dict

#@ ensures \result == 3
def f() -> int:
    d: Dict[int, int] = {1: 1, 2: 0}
    k = 1
    d[k] += 2
    return d[1]

if __name__ == "__main__":
    assert f() == 3
