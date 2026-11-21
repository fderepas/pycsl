r"""Test 6205 -- route #411 (expected FAIL): `requires s == "\n"`, `ensures \result == 4` over `len(s)` (CPython 1; PROVED at base 77b33f239: Why3 1.8.2 prints `"\n"` to Z3 as `\x0A`, which SMT-LIB 2.6 reads as FOUR characters).
"""
# pycsl-expected: FAIL
#@ requires s == "\n"
#@ ensures \result == 4
def f(s: str) -> int:
    return len(s)


if __name__ == "__main__":
    r = f("\n")
    print("VIOLATION ensures" if r != 4 else "result", r)
