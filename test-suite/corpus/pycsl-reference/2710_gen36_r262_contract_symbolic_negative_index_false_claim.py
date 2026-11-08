r"""Test 2710 — route #262 (expected FAIL): a contract-side `xs[k]` with a SYMBOLIC `k == -1`
lowered to the raw logic read `xs[k]` — a map cell no list store touches — so
`ensures xs[k] == \old(xs[k])` PROVED over `xs[1] = 7` at b35d9c5e (a literal `xs[-1]` was
already normalised). CPython: xs[-1] goes 0 -> 7. Now `xs[if k < 0 then len + k else k]`.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2 and k == -1
#@ requires xs[1] == 0
#@ ensures xs[k] == \old(xs[k])
#@ assigns xs[1]
def f(xs: List[int], k: int) -> None:
    xs[1] = 7


if __name__ == "__main__":
    xs = [0, 0]
    f(xs, -1)
    assert xs[-1] == 7
