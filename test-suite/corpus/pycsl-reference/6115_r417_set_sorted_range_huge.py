r"""Test 6115 -- route #417 (expected FAIL): `set(sorted(range(n)))`, `requires n >= 0`, under `no_exception \all`, f(10**20): the argument coerced to `(any int)` erased the Py_ssize_t obligation (CPython OverflowError). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    s = set(sorted(range(n)))
    return 0


if __name__ == "__main__":
    try:
        print(f(10**20))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
