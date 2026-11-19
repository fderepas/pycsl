r"""Test 4127 -- gen #37 route #320 (expected PASS): CONTROL: iterating a list and rebinding it to a literal AFTER the loop is not refused; `\result == 10` proves.
"""
# pycsl-expected: PASS
from typing import List

#@ ensures \result == 10
def f() -> int:
    xs = [1, 2, 3, 4]
    t = 0
    #@ loop invariant 0 <= t
    for x in xs:
        t += x
    xs = [5, 5, 5, 5]
    return xs[0] * 2

if __name__ == "__main__":
    assert f() == 10, f()
