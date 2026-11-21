r"""Test 3344 -- route #287 (expected FAIL): census sibling: `try: return sorted(xs, key=lambda v: d[v]) except KeyError: return []` PROVED `len(\result) == len(xs)`; CPython returns [] for `([1], {})`.
Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ ensures \length(\result) == \length(xs)
def f(xs: List[int], d: Dict[int, int]) -> List[int]:
    try:
        return sorted(xs, key=lambda v: d[v])
    except KeyError:
        return []


if __name__ == "__main__":
    assert len(f([1], {})) == 0
