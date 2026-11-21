r"""Test 2737 — route #261 CONTROL (expected PASS): the same self-call while the invariant
HOLDS (n = 5) still proves `\result >= 0`; CPython returns 5.
"""
#@ class invariant self.n >= 0
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def peek(self) -> int:
        return self.n

    #@ ensures \result >= 0
    #@ assigns self.n
    def a(self) -> int:
        self.n = 5
        r = self.peek()
        self.n = 0
        return r

if __name__ == "__main__":
    print(C().a())
