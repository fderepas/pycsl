r"""Test 3345 -- route #287 (expected PASS): CONTROLS: a raise-free key lambda (`v + 1`, `-v`) under `no_exception \all` keeps its length/permutation claim; `key=None` and `reverse=False` keep the ascending model.
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
#@ ensures \length(\result) == \length(xs)
def plus_one_key(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: v + 1)


#@ no_exception \all
#@ ensures \length(\result) == \length(xs)
def neg_key(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: -v)


#@ ensures \result[0] <= \result[1]
def none_key() -> List[int]:
    return sorted([2, 1], key=None, reverse=False)


if __name__ == "__main__":
    assert len(plus_one_key([3, 1])) == 2
    assert neg_key([1, 3]) == [3, 1]
    assert none_key() == [1, 2]
