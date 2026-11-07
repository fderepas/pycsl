r"""Test 5467 -- gen #37 systematic rule SB (expected PASS): CONTROL: builtins called with EXPLICIT arguments (`max(a, b)`, `min(a, b)`) still prove (CPython 3, 1).
"""
# pycsl-expected: PASS

#@ ensures \result >= a and \result >= b
def g(a: int, b: int) -> int:
    return max(a, b)

#@ ensures \result <= a and \result <= b
def h(a: int, b: int) -> int:
    return min(a, b)

if __name__ == "__main__":
    assert g(1, 3) == 3 and h(1, 3) == 1
