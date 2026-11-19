r"""Test 5380 -- gen #37 route #381 (expected FAIL): NEW shape: `d: MappingProxyType`, `{d: 1}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from types import MappingProxyType

#@ no_exception \all
#@ ensures \result == 1
def g(d: MappingProxyType) -> int:
    m = {d: 1}
    return 1

if __name__ == "__main__":
    print(g(MappingProxyType({})))
