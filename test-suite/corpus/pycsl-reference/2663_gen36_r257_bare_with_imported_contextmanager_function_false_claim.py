r"""Test 2663 — route #257 (expected FAIL): a bare `with bump(b):` over an IMPORTED
module-level `@contextmanager` function that writes its argument's field. CPython: f() == 1.
Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_bumplib import Box, bump


#@ ensures \result == 0
def f() -> int:
    b = Box()
    with bump(b):
        pass
    return b.n


if __name__ == "__main__":
    assert f() == 1
