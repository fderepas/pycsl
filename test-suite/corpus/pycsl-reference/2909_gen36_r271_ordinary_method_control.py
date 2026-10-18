r"""Test 2909 — route #271 CONTROL (expected PASS): 2905 with the advice followed — `bump` is an
ORDINARY method (no `yield`), so the call does run the body and `\result == 1` is TRUE.
CPython `f()` = 1.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> None:
        self.n = self.n + 1

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    c.bump()
    return c.n

if __name__ == "__main__":
    print(f())
