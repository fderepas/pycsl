r"""Test 4826 -- gen #37 route #358 (expected FAIL): NEW latent: `s.startswith(x)`, `x: Any`, under `no_exception \all`; PROVED (CPython TypeError for `f("a", 3)`). FAIL (PyCSL-R358: a str method handed an erased argument).
"""
# pycsl-expected: FAIL
from typing import Any

#@ no_exception \all
def f(s: str, x: Any) -> int:
    if s.startswith(x):
        return 1
    return 0


if __name__ == "__main__":
    try:
        f("a", 3)
        assert False, "expected TypeError"
    except TypeError:
        pass
