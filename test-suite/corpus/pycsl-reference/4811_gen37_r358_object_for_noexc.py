r"""Test 4811 -- gen #37 route #358 (expected FAIL): witness r24: `for z in x`, `x: object`, under `no_exception \all`; PROVED (CPython TypeError). FAIL (PyCSL-R358).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: object) -> int:
    n = 0
    for z in x:
        n = n + 1
    return n


if __name__ == "__main__":
    try:
        f(object())
        assert False, "expected TypeError"
    except TypeError:
        pass
