r"""Test 9070 -- u30 route #568 (expected PASS): CONTROL: a function that reads attribute state (`getattr`) under
`assigns \nothing` and makes no method call keeps its empty frame: the repair adds no effect where no call is.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == n + 1
#@ assigns \nothing
def helper(n: int) -> int:
    return n + 1


#@ ensures \result == 3
#@ assigns \nothing
def caller(o: Any) -> int:
    x = getattr(o, "flag", 0)
    return helper(2)


if __name__ == "__main__":
    print(caller(object()))
