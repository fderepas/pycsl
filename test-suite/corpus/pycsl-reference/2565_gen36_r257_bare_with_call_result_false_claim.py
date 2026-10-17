r"""Test 2565 — route #257 (expected FAIL): a bare `with same(c):` whose context expression
is the RESULT OF A PLAIN CALL returning an imported context-manager instance. CPython:
`Counter.__enter__` runs on the returned object, f() == 1. Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_cmlib import Counter


#@ ensures \result == c
#@ assigns \nothing
def same(c: Counter) -> Counter:
    return c


#@ ensures \result == 0
def f() -> int:
    c = Counter()
    with same(c):
        pass
    return c.n


if __name__ == "__main__":
    assert f() == 1
