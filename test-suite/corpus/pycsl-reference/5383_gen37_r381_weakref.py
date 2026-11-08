r"""Test 5383 -- gen #37 route #381 (expected FAIL): NEW shape: `d: weakref.ref` (hash delegates to the referent), `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
import weakref

class D:
    __hash__ = None

#@ no_exception \all
#@ ensures \result == 1
def g(d: weakref.ref) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(weakref.ref(D())))
