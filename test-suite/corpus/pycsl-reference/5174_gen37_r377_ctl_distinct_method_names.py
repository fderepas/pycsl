r"""Test 5174 -- gen #37 route #377 (expected PASS): CONTROL: distinct method names in a class body: `c.get() + c.get1() == 5` (CPython ok).
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n = 2

    #@ ensures \result == self.n
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

    #@ ensures \result == self.n + 1
    #@ assigns \nothing
    def get1(self) -> int:
        return self.n + 1

#@ ensures \result == 5
def f() -> int:
    c = C()
    return c.get() + c.get1()

if __name__ == "__main__":
    print(f())
