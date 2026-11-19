r"""Test 6114 -- route #417 (expected FAIL): `xs = [*range(n)]` lowered as a ONE-element list: `len(xs) == 1` (CPython n). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
def f(n: int) -> int:
    xs = [*range(n)]
    return len(xs)


if __name__ == "__main__":
    print(f(3))
