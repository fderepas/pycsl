r"""Test 2773 — route #263 (expected FAIL): free function `g` -> method `c.m` on a fresh
instance -> `g`. The `g -> c.m` edge was a stub, so neither `let` saw the cycle: PROVED
`\result == 3` at 283d1033. CPython: RecursionError. Now refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return g(k)

#@ ensures \result == 3
#@ assigns \nothing
def g(k: int) -> int:
    c = C()
    return c.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(g(1))
    except RecursionError:
        print("RecursionError")
