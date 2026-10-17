r"""Test 2562 — route #257 (expected FAIL): a bare `with b.bump():` over an IMPORTED class's
`@contextmanager` method that writes `self.n`. CPython: f() == 1. Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_boxlib import Box


#@ ensures \result == 0
def f() -> int:
    b = Box()
    with b.bump():
        pass
    return b.n


if __name__ == "__main__":
    assert f() == 1
