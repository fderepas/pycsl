r"""Test 2770 — route #263 (expected FAIL): `m` recurses on itself through `self.m(k)` with
no termination measure. The call was a bodyless stub carrying `m`'s own `ensures`, so the
plain `let` claimed termination and assumed `\result == 0` circularly: PROVED at 283d1033.
CPython: RecursionError. Now refused (PYCSL-SEM-METHOD-RECURSION-UNCHECKED).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
