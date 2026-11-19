r"""Test 2772 — route #263 (expected FAIL): `a <-> b` mutual recursion through `self.` calls,
no variant, no `\diverges`. Each stub assumed the other's `\result == 5`: PROVED at 283d1033.
CPython: RecursionError. Now refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 5
    #@ assigns \nothing
    def a(self, k: int) -> int:
        return self.b(k)

    #@ ensures \result == 5
    #@ assigns \nothing
    def b(self, k: int) -> int:
        return self.a(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().a(1))
    except RecursionError:
        print("RecursionError")
