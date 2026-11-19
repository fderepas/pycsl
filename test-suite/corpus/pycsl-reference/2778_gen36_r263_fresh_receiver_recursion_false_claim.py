r"""Test 2778 — route #263 (expected FAIL): `m` recurses through a FRESH receiver,
`C().m(k)` (the IR's `receiver` form); the claim `\result == 0` needs nothing from the
call, only that it RETURNS. PROVED at 283d1033. CPython: RecursionError. Refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        C().m(k)
        return 0

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
