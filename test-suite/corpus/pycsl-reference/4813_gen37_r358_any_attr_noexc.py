r"""Test 4813 -- gen #37 route #358 (expected FAIL): witness r32: `x.foo`, `x: Any`, under `no_exception \all`; PROVED (CPython AttributeError for `f(1)`). FAIL (PyCSL-R358).
"""
# pycsl-expected: FAIL
from typing import Any

#@ no_exception \all
def f(x: Any) -> int:
    y = x.foo
    return 0


if __name__ == "__main__":
    try:
        f(1)
        assert False, "expected AttributeError"
    except AttributeError:
        pass
