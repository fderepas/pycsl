r"""Test 2885 — route #269 R4 (expected FAIL): `m` is `#@ \diverges` AND `#@ no_exception
\all`, and recurses on itself without end. PROVED at 8b0bfbbd: `\all` is the Phase-1 set,
which does not contain RecursionError — and an unbounded Python recursion does not run
forever, it raises exactly that. CPython: RecursionError. Now refused
(PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    #@ no_exception \all
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
