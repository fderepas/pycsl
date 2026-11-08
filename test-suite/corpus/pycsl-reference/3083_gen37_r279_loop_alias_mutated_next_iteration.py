r"""Test 3083 — route #279 (expected FAIL): the alias `b = a` is bound at the END of a loop body and
mutated at the TOP of the next iteration — no statement follows the binding, so a fence over the
statements after it saw nothing; `len(a) == 1` PROVED at 72ab1c57. CPython: 2. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1]
    b: List[int] = []
    for i in range(2):
        b.append(i)
        b = a
    return len(a)


if __name__ == "__main__":
    assert f() == 2
