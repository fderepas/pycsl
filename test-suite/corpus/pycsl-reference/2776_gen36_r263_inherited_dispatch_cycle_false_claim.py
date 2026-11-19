r"""Test 2776 — route #263 (expected FAIL): `B.m` calls the INHERITED `self.p`, which calls
`self.m` — dispatching back to `B.m` on a `B`. The cycle exists only through dynamic dispatch
(`A.p` names `A.m` statically). CPython: RecursionError. Refused: a `self.` receiver resolves
over the class's whole hierarchy.
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def p(self, k: int) -> int:
        return self.m(k)

class B(A):
    def __init__(self) -> None:
        self.n: int = 1

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return self.p(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(B().m(1))
    except RecursionError:
        print("RecursionError")
