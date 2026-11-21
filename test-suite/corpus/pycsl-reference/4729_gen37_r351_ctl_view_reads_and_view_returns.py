r"""Test 4729 -- gen #37 route #351 (expected PASS): CONTROL: reading a view, and returning a view where the return annotation is itself a read-only view (`-> Sequence[int]`, `-> Mapping[str, int]`), stay admitted and prove.
"""
# pycsl-expected: PASS
from typing import Sequence, Mapping

#@ requires len(xs) > 0
#@ ensures \result == xs[0]
def first(xs: Sequence[int]) -> int:
    return xs[0]

#@ ensures \result == xs
def same(xs: Sequence[int]) -> Sequence[int]:
    return xs

#@ ensures \result == d
def same_map(d: Mapping[str, int]) -> Mapping[str, int]:
    return d

if __name__ == "__main__":
    assert first((3, 4)) == 3 and same((1,)) == (1,) and same_map({"a": 1}) == {"a": 1}
