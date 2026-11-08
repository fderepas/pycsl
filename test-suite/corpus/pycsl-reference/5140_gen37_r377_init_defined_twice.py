r"""Test 5140 -- gen #37 route #377 (expected FAIL): two `def __init__` in a class body: the constructor goal `n = 7 -> n >= 5` came from the dead FIRST def (CPython runs the last: `C().get()` is 0, violating the invariant). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = 7

    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

if __name__ == "__main__":
    print(C().get())
