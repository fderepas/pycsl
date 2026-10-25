r"""Test 5172 -- gen #37 route #380 (expected PASS): CONTROL: `super().__init__(3)` matching `B.__init__(self, x)`: `C().x == 3` (CPython ok).
"""
# pycsl-expected: PASS
class B:
    def __init__(self, x: int) -> None:
        self.x = x

class C(B):
    def __init__(self) -> None:
        super().__init__(3)

#@ ensures \result == 3
def f() -> int:
    c = C()
    return c.x

if __name__ == "__main__":
    print(f())
