r"""Test 3785 -- gen #37 route #305 (expected FAIL): a class NESTED in a class body, `A.KeyError(Exception)`, raised under `except LookupError` under `no_exception \all`; the class statement binds a builtin exception name and is refused at any depth (route #305).
"""
# pycsl-expected: FAIL
class A:
    class KeyError(Exception):
        pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise A.KeyError("x")
    except LookupError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
