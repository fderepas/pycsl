r"""Test 5381 -- gen #37 route #381 (expected FAIL): NEW shape: `d: memoryview` (writable: ValueError), `{d}` (CPython ValueError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 1
def g(d: memoryview) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(memoryview(bytearray(2))))
