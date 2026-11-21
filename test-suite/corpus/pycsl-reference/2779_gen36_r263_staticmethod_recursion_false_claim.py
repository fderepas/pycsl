r"""Test 2779 — route #263 (expected FAIL): a `@staticmethod` recursing through its class
name, `C.m(k)` — the shape of the mirror's `IRScanner` walkers; `\result == 0` needs only
that the call RETURNS. PROVED at 283d1033. CPython: RecursionError. Refused.
"""
# pycsl-expected: FAIL
class C:
    #@ ensures \result == 0
    #@ assigns \nothing
    @staticmethod
    def m(k: int) -> int:
        C.m(k)
        return 0

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C.m(1))
    except RecursionError:
        print("RecursionError")
