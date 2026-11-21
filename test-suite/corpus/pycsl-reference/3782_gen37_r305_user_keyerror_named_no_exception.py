r"""Test 3782 -- gen #37 route #305 (expected FAIL): the named `no_exception KeyError` variant: a user `class KeyError(Exception)` raised under `except LookupError` PROVED `\result == 7` and the named claim while CPython escapes; refused by route #305.
"""
# pycsl-expected: FAIL
class KeyError(Exception):
    pass

#@ no_exception KeyError
#@ ensures \result == 7
def g(x: int) -> int:
    r = 0
    try:
        if x < 0:
            raise KeyError("x")
        r = 7
    except LookupError:
        r = 7
    return r

if __name__ == "__main__":
    assert g(-1) == 7
