r"""Test 4116 -- gen #37 route #318 (expected PASS): CONTROL: `for i in range(len(xs)): xs.append(0)` over a seq-promoted list runs `len` of the ORIGINAL list times; `\result == 2` proves.
"""
# pycsl-expected: PASS
from typing import List

#@ ensures \result == 2
def f() -> int:
    xs = [1, 2]
    c = 0
    #@ loop invariant 0 <= i <= 2
    #@ loop invariant c == i
    #@ loop variant 3 - i
    for i in range(len(xs)):
        xs.append(0)
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 2, f()
