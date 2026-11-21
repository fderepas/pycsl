r"""Test 2711 — route #262 (expected FAIL): `\result[k]` on a list return took the
`\result`-array arm, which never normalised any index, so the raw cell `-1` was compared
with the raw `\old(xs[-1])` cell and PROVED at b35d9c5e. CPython: \result[-1] == 7 != 0.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2 and k == -1
#@ requires xs[1] == 0
#@ ensures \result[k] == \old(xs[k])
#@ assigns xs[1]
def f(xs: List[int], k: int) -> List[int]:
    xs[1] = 7
    return xs


if __name__ == "__main__":
    r = f([0, 0], -1)
    assert r[-1] == 7
