r"""Test 4527 -- gen #37 route #336 (expected PASS): CONTROL: a READ of `xs: Tuple[str, ...]` PROVES.
"""
# pycsl-expected: PASS
from typing import Tuple

#@ requires len(xs) > 0
#@ ensures \result == xs[0]
def first(xs: Tuple[str, ...]) -> str:
    return xs[0]

if __name__ == "__main__":
    assert first(("a",)) == "a"
