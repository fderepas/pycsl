r"""Test 3781 -- gen #37 route #305 (expected FAIL): a user `class LookupError(Exception)` handler "caught" the builtin `KeyError` (the model gave the user class the builtin hierarchy) and `no_exception \all` PROVED while CPython escapes; refused by route #305.
"""
# pycsl-expected: FAIL
class LookupError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
