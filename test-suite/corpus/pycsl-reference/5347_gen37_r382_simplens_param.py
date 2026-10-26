r"""Test 5347 -- gen #37 route #382 (expected FAIL): `d: SimpleNamespace`, `{d}` (CPython TypeError; PROVED at base 7bf752d4e).
"""
# pycsl-expected: FAIL
from types import SimpleNamespace

#@ no_exception \all
#@ ensures \result == 1
def g(d: SimpleNamespace) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(SimpleNamespace()))
