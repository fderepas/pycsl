r"""Test 4523 -- gen #37 route #336 (expected PASS): CONTROL: a READ of `xs: Sequence[int]` (`xs[0] + 1`) PROVES (read as `List[int]`).
"""
# pycsl-expected: PASS
from typing import Sequence

#@ requires len(xs) > 0
#@ ensures \result == xs[0] + 1
def head1(xs: Sequence[int]) -> int:
    return xs[0] + 1

if __name__ == "__main__":
    assert head1([3]) == 4
