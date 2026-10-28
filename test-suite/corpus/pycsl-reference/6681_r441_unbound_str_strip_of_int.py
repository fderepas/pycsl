r"""Test 6681 -- route #441 (expected FAIL): the UNBOUND builtin method `str.strip(n)` with `n: int` under `#@ no_exception \all`. Its receiver argument must be derived as exactly `str`; CPython raises TypeError (descriptor 'strip' for 'str' objects doesn't apply to a 'int' object; the `__main__` driver prints VIOLATION). REFUSED (PYCSL-R441-BUILTIN-SIGNATURE).
"""
# pycsl-expected: FAIL


#@ no_exception \all
def f(n: int) -> int:
    return len(str.strip(n))


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
