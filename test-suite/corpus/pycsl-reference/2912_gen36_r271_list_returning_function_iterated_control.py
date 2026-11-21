r"""Test 2912 — route #271 CONTROL (expected PASS): the refusal's advice followed — a producer of
values written as an ORDINARY function that RETURNS a `list`, which the caller iterates; the
loop's own counter is what the caller proves. CPython `f()` = 2.
"""
# pycsl-expected: PASS
from typing import List

#@ assigns \nothing
def vals() -> List[int]:
    return [1, 2]

#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    k = 0
    #@ loop invariant k >= 0
    for x in vals():
        k = k + 1
    return k

if __name__ == "__main__":
    print(f())
