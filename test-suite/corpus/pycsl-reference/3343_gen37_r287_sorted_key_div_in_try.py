r"""Test 3343 -- route #287 (expected FAIL): `try: return sorted(xs, key=lambda v: 10 // v) except ZeroDivisionError: return []` PROVED `len(\result) == len(xs)` (the handler is dead in the model); CPython returns [] for `[0]`.
Now refused (the handler widens the context, route #171, and the lambda body divides).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \length(\result) == \length(xs)
def f(xs: List[int]) -> List[int]:
    try:
        return sorted(xs, key=lambda v: 10 // v)
    except ZeroDivisionError:
        return []


if __name__ == "__main__":
    assert len(f([0])) == 0
