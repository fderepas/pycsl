r"""Test 5379 -- gen #37 route #381 (expected FAIL): NEW shape: `d: types.MappingProxyType`, `{d}` (its `__hash__` delegates to the mapping) (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
import types

#@ no_exception \all
#@ ensures \result == 1
def g(d: types.MappingProxyType) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(types.MappingProxyType({})))
