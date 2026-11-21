r"""Test 2777 — route #263 (expected FAIL): `__init__` calls `self.m`, and `m` constructs a
fresh `C()`. Module 5 keeps only the `self.f = <param>` bindings of `__init__`, so the cycle
`m -> C() -> __init__ -> m` was invisible. CPython: RecursionError. Refused: the constructor's
calls are read from the source.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0
        self.m(1)

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        c = C()
        return 0

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
