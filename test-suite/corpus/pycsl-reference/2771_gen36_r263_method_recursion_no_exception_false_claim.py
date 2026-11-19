r"""Test 2771 — route #263 (expected FAIL): the 2770 shape under `#@ no_exception \all`.
PROVED at 283d1033; CPython raises RecursionError (unbounded self-recursion). Now refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
