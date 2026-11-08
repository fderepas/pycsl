r"""Test 2718 — route #262 CONTROL (expected PASS): a symbolic `xs[k]` under
`requires 0 <= k` normalises to `k` itself; the TRUE claim proves.
"""
from typing import List


#@ requires len(xs) == 2 and 0 <= k and k < 2
#@ ensures \result == xs[k]
#@ assigns \nothing
def f(xs: List[int], k: int) -> int:
    return xs[k]


if __name__ == "__main__":
    assert f([3, 4], 1) == 4
