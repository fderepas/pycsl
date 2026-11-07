r"""Test 4523 -- gen #37 route #336 (expected PASS): CONTROL: a READ of `xs: Sequence[int]` (`xs[0] + 1`) and `len` of a read-only view PROVE (read as `List[int]`; passing the view to `len` is not a store).
"""
# pycsl-expected: PASS
from typing import Sequence

#@ requires len(xs) > 0
#@ ensures \result == xs[0] + 1
def head1(xs: Sequence[int]) -> int:
    return xs[0] + 1

#@ ensures \result == len(xs)
def n(xs: Sequence[int]) -> int:
    return len(xs)

if __name__ == "__main__":
    assert head1([3]) == 4
    assert n((1, 2)) == 2
