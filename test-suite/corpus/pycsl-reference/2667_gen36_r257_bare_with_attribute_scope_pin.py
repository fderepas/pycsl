r"""Test 2667 — route #257 SCOPE PIN (expected FAIL): a bare `with h.c:` whose context
expression is an ATTRIBUTE holding an imported context-manager instance. The claim is FALSE
(CPython: `__enter__` bumps `h.c.n`, f() == 1); at 49f6a35d it already FAILED (the
un-contracted `Holder.__init__` leaves `h.c` opaque), so this is not a proved-false witness —
it pins that an attribute context expression is now REFUSED fail-closed, never waved through.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_cmlib import Counter


class Holder:
    def __init__(self) -> None:
        self.c: Counter = Counter()


#@ ensures \result == 0
def f() -> int:
    h = Holder()
    a = h.c.n
    with h.c:
        pass
    return h.c.n - a


if __name__ == "__main__":
    assert f() == 1
