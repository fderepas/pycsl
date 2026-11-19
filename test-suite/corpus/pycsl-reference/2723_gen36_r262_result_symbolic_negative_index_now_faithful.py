r"""Test 2723 — route #262 COVERAGE (expected PASS; FAILED at b35d9c5e): `\result[k]` with
`k == -1` is the last element — the TRUE claim `\result[k] == 7` now proves.
"""
from typing import List


#@ requires len(xs) == 2 and k == -1
#@ ensures \result[k] == 7
#@ assigns xs[1]
def f(xs: List[int], k: int) -> List[int]:
    xs[1] = 7
    return xs


if __name__ == "__main__":
    assert f([0, 0], -1)[-1] == 7
