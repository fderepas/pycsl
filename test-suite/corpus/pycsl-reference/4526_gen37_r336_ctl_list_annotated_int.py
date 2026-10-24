r"""Test 4526 -- gen #37 route #336 (expected PASS): CONTROL: `xs: List[Annotated[int, ..]]` is `List[int]` (`xs[0] + xs[0] == xs[0] * 2` PROVES), and a READ of `ys: Tuple[str, ...]` PROVES.
"""
# pycsl-expected: PASS
from typing import Annotated, List, Tuple

#@ requires len(xs) > 0
#@ ensures \result == xs[0] * 2
def twice(xs: List[Annotated[int, "u"]]) -> int:
    return xs[0] + xs[0]

#@ requires len(ys) > 0
#@ ensures \result == ys[0]
def first(ys: Tuple[str, ...]) -> str:
    return ys[0]

if __name__ == "__main__":
    assert twice([4]) == 8
    assert first(("a",)) == "a"
