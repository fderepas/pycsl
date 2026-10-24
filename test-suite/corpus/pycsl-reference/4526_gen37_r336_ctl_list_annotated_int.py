r"""Test 4526 -- gen #37 route #336 (expected PASS): CONTROL: `xs: List[Annotated[int, ..]]` is `List[int]`; `xs[0] + xs[0] == xs[0] * 2` PROVES.
"""
# pycsl-expected: PASS
from typing import Annotated, List

#@ requires len(xs) > 0
#@ ensures \result == xs[0] * 2
def twice(xs: List[Annotated[int, "u"]]) -> int:
    return xs[0] + xs[0]

if __name__ == "__main__":
    assert twice([4]) == 8
