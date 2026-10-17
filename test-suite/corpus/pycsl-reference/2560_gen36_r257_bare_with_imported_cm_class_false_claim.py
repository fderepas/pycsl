r"""Test 2560 — route #257 (expected FAIL): a bare `with c:` over an IMPORTED context-manager
class whose `__enter__` writes `self.n`. The route #38/#39 guard only looked for a CM class
DEFINED IN THE SAME FILE, so the statement was lowered to its body alone
(`let c = { n = 0 } in (); c.n`) and `\result == 0` PROVED at 49f6a35d.
CPython: `__enter__` runs, f() == 1. Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_cmlib import Counter


#@ ensures \result == 0
def f() -> int:
    c = Counter()
    with c:
        pass
    return c.n


if __name__ == "__main__":
    assert f() == 1
