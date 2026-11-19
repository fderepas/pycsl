r"""Test 5382 -- gen #37 route #381 (expected FAIL): NEW shape: `d: slice` holding a list, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 1
def g(d: slice) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(slice(0, [])))
