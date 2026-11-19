r"""Test 3784 -- gen #37 route #305 (expected FAIL): a FUNCTION-LOCAL `class KeyError(Exception)` raised under `except LookupError` PROVED `no_exception \all` (CPython escapes); a class statement binding a builtin exception name is refused at any depth (route #305).
"""
# pycsl-expected: FAIL
#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    class KeyError(Exception):
        pass
    try:
        if x < 0:
            raise KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
