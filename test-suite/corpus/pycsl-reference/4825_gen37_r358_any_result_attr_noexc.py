r"""Test 4825 -- gen #37 route #358 (expected FAIL): NEW latent: `mk().foo` on a `-> Any` call result under `no_exception \all`; PROVED (CPython AttributeError). FAIL (PyCSL-R358).
"""
# pycsl-expected: FAIL
from typing import Any

def mk() -> Any:
    return object()

#@ no_exception \all
def f() -> int:
    y = mk().foo
    return 0


if __name__ == "__main__":
    try:
        f()
        assert False, "expected AttributeError"
    except AttributeError:
        pass
