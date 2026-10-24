r"""Test 4524 -- gen #37 route #336 (expected PASS): CONTROL: `len(xs)` of `xs: Sequence[int]` PROVES (passing a read-only view to `len` is not a store).
"""
# pycsl-expected: PASS
from typing import Sequence

#@ ensures \result == len(xs)
def n(xs: Sequence[int]) -> int:
    return len(xs)

if __name__ == "__main__":
    assert n((1, 2)) == 2
