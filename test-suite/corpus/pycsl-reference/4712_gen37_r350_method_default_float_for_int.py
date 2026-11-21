r"""Test 4712 -- gen #37 route #350 (expected FAIL): a METHOD `m(self, x: int = 0.5)` PROVED `\result == 0` for `x % 1` (CPython 0.5). REFUSED now (route #350).
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 0
    def m(self, x: int = 0.5) -> int:  # type: ignore
        return x % 1

if __name__ == "__main__":
    print(C().m())
