r"""Test 2735 — route #261 (expected FAIL): `a()` breaks the class invariant (n = -1) and
calls `self.peek()`, whose `\result >= 0` was proved ASSUMING the invariant. The receiver-less
stub `self_peek_0 ()` dropped the invariant check at the call; CPython returns -1. Now the stub
takes `self` and Why3 demands the invariant ("type invariant") at the call.
"""
# pycsl-expected: FAIL
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
        self.n = -1
        r = self.peek()
        self.n = 0
        return r

if __name__ == "__main__":
    print(C().a())
