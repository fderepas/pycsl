r"""Test 3731 -- gen #37 route #304 (expected FAIL): an own `raise ValueError` inside a `try` whose only handler is `except KeyError` escapes the function; under `no_exception \all` it is a reachability obligation and FAILS (CPython raises ValueError).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 0
def g(x: int) -> int:
    try:
        if x < 0:
            raise ValueError("neg")
    except KeyError:
        return 0
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
