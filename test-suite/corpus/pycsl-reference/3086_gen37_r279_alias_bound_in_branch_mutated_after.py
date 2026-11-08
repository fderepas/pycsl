r"""Test 3086 — route #279 (expected FAIL): the alias is bound inside an `if` and mutated AFTER it —
outside the binding's own block, so a fence over the statements after the binding saw nothing;
`len(a) == 1` PROVED at 72ab1c57 (census probe q27). CPython: 2. Now refused (escaping alias).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f(c: bool) -> int:
    a: List[int] = [1]
    b: List[int] = [7]
    if c:
        b = a
    b.append(2)
    return len(a)


if __name__ == "__main__":
    assert f(True) == 2
