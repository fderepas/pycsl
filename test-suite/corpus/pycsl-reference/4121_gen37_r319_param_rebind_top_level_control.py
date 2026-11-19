r"""Test 4121 -- gen #37 route #319 (expected PASS): CONTROL: a parameter rebound at the TOP level of the body (`xs = [7, 7, 7]`) is a `let` scoping the rest of the function; `\result == 3` proves.
"""
# pycsl-expected: PASS
from typing import List

#@ requires len(xs) == 2
#@ ensures \result == 3
def f(xs: List[int]) -> int:
    xs = [7, 7, 7]
    return len(xs)

if __name__ == "__main__":
    assert f([1, 2]) == 3, f([1, 2])
