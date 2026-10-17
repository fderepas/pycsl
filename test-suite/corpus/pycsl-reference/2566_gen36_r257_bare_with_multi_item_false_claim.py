r"""Test 2566 — route #257 (expected FAIL): a MULTI-ITEM bare `with c, d:` over two imported
context-manager instances; both `__enter__` calls were erased. CPython: f() == 2.
Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_cmlib import Counter


#@ ensures \result == 0
def f() -> int:
    c = Counter()
    d = Counter()
    with c, d:
        pass
    return c.n + d.n


if __name__ == "__main__":
    assert f() == 2
