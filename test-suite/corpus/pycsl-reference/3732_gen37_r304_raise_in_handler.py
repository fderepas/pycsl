r"""Test 3732 -- gen #37 route #304 (expected FAIL): the handler of a locally caught `ValueError` raises `KeyError`, which escapes; under `no_exception \all` the handler's raise is a reachability obligation and FAILS (CPython raises KeyError).
"""
# pycsl-expected: FAIL


#@ no_exception \all
#@ ensures \result == 0
def g(x: int) -> int:
    try:
        if x < 0:
            raise ValueError("neg")
    except ValueError:
        raise KeyError("k")
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
