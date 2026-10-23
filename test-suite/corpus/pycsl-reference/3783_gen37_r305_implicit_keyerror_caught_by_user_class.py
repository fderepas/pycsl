r"""Test 3783 -- gen #37 route #305 (expected FAIL): the IMPLICIT builtin KeyError of `d[5]` was "caught" by `except KeyError` naming the user `class KeyError(Exception)` (one shared tag), so `no_exception \all` PROVED while CPython escapes; refused by route #305.
"""
# pycsl-expected: FAIL
from typing import Dict
class KeyError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: Dict[int, int]) -> int:
    try:
        y = d[5]
    except KeyError:
        return 1
    return 1

if __name__ == "__main__":
    assert g({}) == 1
