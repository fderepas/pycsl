r"""Test 5554 -- gen #37 route #392 (expected FAIL): NEW LATENT (hash MRO): `from typing import TypedDict` + a nested `class TypedDict` + module `class T(TypedDict)` (a modelled base, admitted by S1) hashed by `{t}` (an instance is a `dict`) (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the hash MRO reads the base as `typing.TypedDict`).
"""
# pycsl-expected: FAIL
from typing import TypedDict


def _unused() -> int:
    class TypedDict:
        pass
    return 0


class T(TypedDict):
    x: int


#@ no_exception \all
def f(t: T) -> int:
    s = {t}
    return len(s)
