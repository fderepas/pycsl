r"""Test 4812 -- gen #37 route #358 (expected FAIL): witness r25: `x.foo`, `x: object`, under `no_exception \all`; PROVED (CPython AttributeError). FAIL (PyCSL-R358).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(x: object) -> int:
    y = x.foo
    return 0


if __name__ == "__main__":
    try:
        f(object())
        assert False, "expected AttributeError"
    except AttributeError:
        pass
