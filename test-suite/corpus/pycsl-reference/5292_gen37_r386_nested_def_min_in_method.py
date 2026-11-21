r"""Test 5292 -- gen #37 route #386 (expected FAIL): `def min(x, y): return 100` nested in a method, `min(self.a, 1) <= 1`; PROVED at base (CPython 100). REFUSED (route #386).
"""
# pycsl-expected: FAIL
class W:
    def __init__(self) -> None:
        self.a: int = 3

    #@ ensures \result <= 1
    #@ assigns \nothing
    def m(self) -> int:
        def min(x: int, y: int) -> int:
            return 100
        return min(self.a, 1)


if __name__ == "__main__":
    r = W().m()
    print("VIOLATION m() =", r) if r > 1 else print("no violation")
