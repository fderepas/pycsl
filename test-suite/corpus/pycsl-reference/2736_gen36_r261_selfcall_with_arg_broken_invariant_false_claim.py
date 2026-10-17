r"""Test 2736 — route #261 (expected FAIL): the same with an argument and a callee
precondition: `self.peek(1)` with `self.n == -3`; CPython returns -2. Now refused at the call
("type invariant").
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 0
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires k >= 0
    #@ ensures \result >= k
    #@ assigns \nothing
    def peek(self, k: int) -> int:
        return self.n + k

    #@ ensures \result >= 0
    #@ assigns self.n
    def a(self) -> int:
        self.n = -3
        r = self.peek(1)
        self.n = 0
        return r

if __name__ == "__main__":
    print(C().a())
