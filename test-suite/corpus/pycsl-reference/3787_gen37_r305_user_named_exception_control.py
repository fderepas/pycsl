r"""Test 3787 -- gen #37 route #305 (expected PASS): control: a user exception with its OWN name (`MyKeyError(Exception)`) raised and caught by its own handler under `no_exception \all` must still PROVE.
"""
class MyKeyError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise MyKeyError("x")
    except MyKeyError:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
