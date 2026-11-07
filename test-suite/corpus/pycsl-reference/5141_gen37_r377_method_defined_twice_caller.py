r"""Test 5141 -- gen #37 route #377 (expected FAIL): two `def get`: `c.get()` used the first def's `ensures \result == 1` while the emitted body is the last def (CPython 2). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self) -> int:
        return 1

    def get(self) -> int:
        return 2

#@ ensures \result == 1
def f(c: C) -> int:
    return c.get()

if __name__ == "__main__":
    print(f(C()))
