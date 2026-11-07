r"""Test 3938 -- gen #37 route #308 (expected PASS): CONTROL: `ys[len(ys) - 1] += 3` (pure builtin in the index) keeps today's lowering and proves.
"""
# pycsl-expected: PASS
from typing import List

#@ ensures \result == 6
def f() -> int:
    ys = [1, 2, 3]
    ys[len(ys) - 1] += 3
    return ys[2]

if __name__ == "__main__":
    assert f() == 6
