r"""Test 2721 — route #262 COVERAGE (expected PASS; FAILED at b35d9c5e): with Python's index
in contracts, the TRUE claim `xs[k] == 7` for `k == -1` after `xs[1] = 7` now proves.
"""
from typing import List


#@ requires len(xs) == 2 and k == -1
#@ ensures xs[k] == 7
#@ assigns xs[1]
def f(xs: List[int], k: int) -> None:
    xs[1] = 7


if __name__ == "__main__":
    xs = [0, 0]
    f(xs, -1)
    assert xs[-1] == 7
