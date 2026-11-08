r"""Test 2717 — route #262 CONTROL (expected PASS): a literal `xs[-1]` keeps its
`len - 1` rewrite and the TRUE claim proves.
"""
from typing import List


#@ requires len(xs) == 2
#@ ensures \result == xs[-1]
#@ assigns \nothing
def f(xs: List[int]) -> int:
    return xs[1]


if __name__ == "__main__":
    assert f([3, 4]) == 4
