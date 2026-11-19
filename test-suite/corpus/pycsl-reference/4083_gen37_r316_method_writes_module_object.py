r"""Test 4083 -- gen #37 route #316 (expected FAIL): method does `gq.n += 1` on a module-level object; `gq.n - a == 0` PROVED (CPython 1). REFUSED: PYCSL-METHOD-GLOBAL-WRITE.
"""
# pycsl-expected: FAIL
class Q:
    def __init__(self) -> None:
        self.n = 0

gq = Q()

class P:
    def __init__(self) -> None:
        self.c = 0
    def bump(self) -> None:
        gq.n = gq.n + 1

#@ ensures \result == 0
def f() -> int:
    a = gq.n
    p = P()
    p.bump()
    return gq.n - a

if __name__ == "__main__":
    assert f() == 0, f()
