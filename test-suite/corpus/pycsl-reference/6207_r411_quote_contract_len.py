r"""Test 6207 -- route #411 (expected FAIL): `requires s == "a\"b"`, `ensures \result == 6` over `len(s)` (CPython 3; PROVED at base 77b33f239: `"` was printed `\x22`, four characters to Z3).
"""
# pycsl-expected: FAIL
#@ requires s == "a\"b"
#@ ensures \result == 6
def f(s: str) -> int:
    return len(s)


if __name__ == "__main__":
    r = f("a\"b")
    print("VIOLATION ensures" if r != 6 else "result", r)
